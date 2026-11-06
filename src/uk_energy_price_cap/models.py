"""The reform model, copied from the Autumn Budget 2026 pipeline.

A reform is either parameter changes (simple reforms) or a simulation
modifier (structural reforms), against current law or against its own
baseline. The event fields below it (route, status, limits) are what the
coverage ledger and the publication gate read.

``policyengine_uk`` is imported only when a scenario is built, so the
registry, the tests and the placeholder pipeline run without the model.
"""

from enum import StrEnum
from typing import Any, Callable, Optional

from pydantic import BaseModel, Field, model_validator


class Route(StrEnum):
    """Route class of a ledger line (docs/DRILL.md)."""

    DASHBOARD_PARAM = "dashboard-param"
    DASHBOARD_STRUCTURAL = "dashboard-structural"
    LEDGER = "ledger"
    NOT_COMPUTABLE = "not-computable"
    NEEDS_PE_UK_FIRST = "needs-pe-uk-first"


class Status(StrEnum):
    """Where a measure stands.

    ``announced`` is published with figures. ``withdrawn`` keeps the
    ledger line (and its card) with no figures, for a candidate lever that
    was not announced on the day, so no registry entry needs deleting
    under time pressure. ``placeholder`` holds the file back as a
    placeholder.
    """

    PLACEHOLDER = "placeholder"
    ANNOUNCED = "announced"
    WITHDRAWN = "withdrawn"


class Reform(BaseModel):
    """Definition of a policy reform and its place in the ledger."""

    id: str = Field(..., description="Unique identifier for the reform")
    name: str = Field(..., description="Human-readable name")
    description: str = Field(
        default="", description="Detailed description of the reform"
    )
    parameter_changes: Optional[dict[str, dict[str, Any]]] = Field(
        default=None,
        description="Parameter path -> {period: value} mappings for reform",
    )
    baseline_parameter_changes: Optional[dict[str, dict[str, Any]]] = Field(
        default=None,
        description=(
            "Parameter changes for a custom baseline. If provided, both "
            "baseline and reform use the modified parameters."
        ),
    )
    baseline_simulation_modifier: Optional[Callable] = Field(
        default=None,
        description="Function that modifies the baseline simulation",
    )
    simulation_modifier: Optional[Callable] = Field(
        default=None,
        description="Function that modifies a simulation object",
    )

    # Event fields. Required, no defaults: every entry states them.
    route: Route
    status: Status
    lever: str = Field(
        ..., description="What moves: 'support' or 'bills' (the cap itself)"
    )
    limit_reason: Optional[str] = Field(
        default=None,
        description="Why the measure is not computable, or what must land first",
    )
    likelihood: str = Field(
        ...,
        description="certain, announced, medium, low (docs/candidate-reforms.md)",
    )
    calculator_only: bool = Field(
        default=False,
        description="Shown in the household calculator only, never charted",
    )

    model_config = {"arbitrary_types_allowed": True}

    @model_validator(mode="after")
    def _route_matches_content(self) -> "Reform":
        computable = self.route in (
            Route.DASHBOARD_PARAM,
            Route.DASHBOARD_STRUCTURAL,
        )
        has_change = (
            self.parameter_changes is not None
            or self.simulation_modifier is not None
        )
        if computable and not has_change:
            raise ValueError(
                f"{self.id}: route {self.route} needs parameter changes or a "
                "modifier"
            )
        if not computable and not self.limit_reason:
            raise ValueError(
                f"{self.id}: route {self.route} needs a limit_reason"
            )
        if self.route == Route.DASHBOARD_PARAM and (
            self.simulation_modifier is not None
        ):
            raise ValueError(
                f"{self.id}: a dashboard-param route takes no modifier"
            )
        return self

    @property
    def is_placeholder(self) -> bool:
        return self.status == Status.PLACEHOLDER

    @property
    def is_computable(self) -> bool:
        return self.route in (
            Route.DASHBOARD_PARAM,
            Route.DASHBOARD_STRUCTURAL,
        )

    def to_scenario(self):
        """Convert this reform to a PolicyEngine Scenario object."""
        from policyengine_uk.utils.scenario import Scenario

        if (
            self.simulation_modifier is not None
            and self.parameter_changes is not None
        ):
            return Scenario(
                simulation_modifier=self.simulation_modifier,
                parameter_changes=self.parameter_changes,
            )
        if self.simulation_modifier is not None:
            return Scenario(simulation_modifier=self.simulation_modifier)
        if self.parameter_changes is not None:
            return Scenario(parameter_changes=self.parameter_changes)
        return Scenario()

    def to_baseline_scenario(self):
        """Baseline parameter changes as a Scenario, or None for current law."""
        if (
            self.baseline_simulation_modifier is None
            and self.baseline_parameter_changes is None
        ):
            return None
        from policyengine_uk.utils.scenario import Scenario

        if (
            self.baseline_simulation_modifier is not None
            and self.baseline_parameter_changes is not None
        ):
            return Scenario(
                simulation_modifier=self.baseline_simulation_modifier,
                parameter_changes=self.baseline_parameter_changes,
            )
        if self.baseline_simulation_modifier is not None:
            return Scenario(
                simulation_modifier=self.baseline_simulation_modifier
            )
        return Scenario(parameter_changes=self.baseline_parameter_changes)

    def has_custom_baseline(self) -> bool:
        return (
            self.baseline_parameter_changes is not None
            or self.baseline_simulation_modifier is not None
        )

    def parameter_paths(self) -> list[str]:
        paths = list(self.parameter_changes or {})
        paths += list(self.baseline_parameter_changes or {})
        return paths
