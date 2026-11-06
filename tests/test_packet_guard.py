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
