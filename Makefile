# One command per gate (docs/RUNBOOK.md). DATASET names the frozen file.
.PHONY: install install-model test lint format generate check ledger freeze build

install:
	uv sync --locked --extra dev
	cd dashboard && bun install --frozen-lockfile

install-model:
	uv sync --locked --extra dev --extra model

test:
	uv run pytest
	cd dashboard && bun run test

lint:
	uv run ruff check .
	uv run ruff format --check .
	cd dashboard && bun run lint

format:
	uv run ruff format .

generate:
ifdef DATASET
	uv run uk-energy-price-cap generate --source model --allow-unmanaged --dataset $(DATASET)
else
	uv run uk-energy-price-cap generate
endif

check:
	uv run uk-energy-price-cap validate
	uv run python scripts/check_public_data.py
	cd dashboard && bun run check-public

ledger:
	uv run uk-energy-price-cap ledger

freeze:
	uv run uk-energy-price-cap freeze $(if $(DATASET),--dataset $(DATASET),)

build:
	cd dashboard && bun run build
