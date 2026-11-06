import hashlib
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _module():
    spec = importlib.util.spec_from_file_location(
        "check_packet", ROOT / "scripts" / "check_packet_not_committed.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_a_tracked_packet_file_fails(tmp_path, monkeypatch):
    module = _module()
    monkeypatch.setattr(module, "ROOT", tmp_path)
    released = tmp_path / "copied.md"
    released.write_text("released text\n")
    other = tmp_path / "other.md"
    other.write_text("other\n")
    digest = hashlib.sha256(released.read_bytes()).hexdigest()
    plan = tmp_path / "DRILL.md"
    plan.write_text(f"| `x.md` | 10:00 | `{digest}` |\n")
    problems = module.check(plan, [released, other, plan])
    assert problems == ["copied.md: a drill packet file"]


def test_no_plan_means_nothing_to_check(tmp_path):
    module = _module()
    assert module.check(tmp_path / "DRILL.md", []) == []


def test_a_drill_branch_with_no_plan_fails(tmp_path):
    module = _module()
    problems = module.check(tmp_path / "DRILL.md", [], drill_branch=True)
    assert len(problems) == 1
    assert "drill-plan -- DRILL.md" in problems[0]


def test_a_drill_branch_with_a_plan_but_no_hashes_fails(tmp_path):
    module = _module()
    plan = tmp_path / "DRILL.md"
    plan.write_text("# Drill\n\nNo hashes here.\n")
    assert module.check(plan, [plan], drill_branch=True) != []


def test_a_drill_branch_with_hashes_and_no_packet_file_passes(
    tmp_path, monkeypatch
):
    module = _module()
    monkeypatch.setattr(module, "ROOT", tmp_path)
    plan = tmp_path / "DRILL.md"
    plan.write_text(f"| `x.md` | 10:00 | `{'0' * 64}` |\n")
    other = tmp_path / "other.md"
    other.write_text("other\n")
    assert module.check(plan, [plan, other], drill_branch=True) == []


def test_branch_name_prefers_the_pull_request_head(tmp_path):
    module = _module()
    env = {"GITHUB_HEAD_REF": "drill-2026-11-13", "GITHUB_REF_NAME": "9/merge"}
    assert module.branch_name(env, tmp_path) == "drill-2026-11-13"
    assert module.branch_name({"GITHUB_REF_NAME": "main"}, tmp_path) == "main"


def test_drill_branch_detection():
    module = _module()
    assert module.is_drill_branch("drill-2026-11-13")
    assert module.is_drill_branch("Drill/ofgem")
    assert not module.is_drill_branch("template-dashboard")
    assert not module.is_drill_branch("main")
    assert not module.is_drill_branch("")
