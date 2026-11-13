"""The heavy-run lock and the run's guards. Every test uses a scratch lock
path; the real /tmp/pe-heavy.lock is never touched."""

import os
import subprocess
import sys
import threading
import time
from contextlib import contextmanager
from pathlib import Path

import pytest

from uk_energy_price_cap import heavy, model_run, pipeline


@pytest.fixture(autouse=True)
def scratch_lock(tmp_path, monkeypatch):
    lock = tmp_path / "pe-heavy.lock"
    monkeypatch.setattr(heavy, "LOCK", lock)
    assert lock != Path("/tmp/pe-heavy.lock")
    return lock


def test_free_lock_is_a_file_with_pid_and_label(scratch_lock):
    with heavy.heavy_lock("energy-test", free_gb=lambda: 99.0):
        assert scratch_lock.is_file()
        assert scratch_lock.read_text().split() == [
            str(os.getpid()),
            "energy-test",
        ]
    assert not scratch_lock.exists()


def test_lock_is_released_when_the_run_fails(scratch_lock):
    with pytest.raises(RuntimeError):
        with heavy.heavy_lock("energy-test", free_gb=lambda: 99.0):
            raise RuntimeError("boom")
    assert not scratch_lock.exists()


def test_a_lock_taken_over_by_another_owner_is_left_alone(scratch_lock):
    with heavy.heavy_lock("energy-test", free_gb=lambda: 99.0):
        scratch_lock.write_text("4242 someone-else\n")
    assert scratch_lock.read_text() == "4242 someone-else\n"


@pytest.mark.parametrize("held_as", ["file", "directory"])
def test_waits_while_another_lock_is_held(scratch_lock, held_as):
    if held_as == "file":
        scratch_lock.write_text("99999 other\n")
    else:
        scratch_lock.mkdir()
    taken = threading.Event()

    def run():
        with heavy.heavy_lock("energy-test", poll=0.05, free_gb=lambda: 99.0):
            taken.set()

    thread = threading.Thread(target=run)
    thread.start()
    time.sleep(0.3)
    assert not taken.is_set()
    if held_as == "file":
        assert scratch_lock.read_text() == "99999 other\n"
        scratch_lock.unlink()
    else:
        scratch_lock.rmdir()
    thread.join(5)
    assert taken.is_set()
    assert not scratch_lock.exists()


def test_memory_gate_waits_for_22_gb_with_the_lock_held(scratch_lock):
    readings = iter([10.0, 21.9, 22.0])
    seen = []

    def free_gb():
        seen.append(scratch_lock.exists())
        return next(readings)

    with heavy.heavy_lock("energy-test", mem_poll=0, free_gb=free_gb):
        pass
    assert heavy.MIN_FREE_GB == 22.0
    assert seen == [True, True, True]


def test_sigterm_releases_the_lock(tmp_path):
    lock = tmp_path / "term.lock"
    code = (
        "import sys, time\n"
        "from uk_energy_price_cap import heavy\n"
        f"with heavy.heavy_lock('energy-test', path={str(lock)!r}, "
        "free_gb=lambda: 99.0):\n"
        "    print('held', flush=True)\n"
        "    time.sleep(30)\n"
    )
    proc = subprocess.Popen(
        [sys.executable, "-c", code], stdout=subprocess.PIPE, text=True
    )
    assert proc.stdout.readline().strip() == "held"
    assert lock.exists()
    proc.terminate()
    proc.wait(10)
    assert not lock.exists()


def _clean_record(versions):
    return {
        "clean": True,
        "versions": versions,
        "dataset": {"build": "b", "sha256": "0" * 64},
    }


def test_national_run_holds_the_lock_for_every_simulation(
    tmp_path, monkeypatch
):
    from test_pipeline import _fake_runner

    dataset = tmp_path / "microcosm.h5"
    dataset.write_bytes(b"x")
    fake = _fake_runner()
    held = []
    labels = []

    @contextmanager
    def fake_lock(label, **kwargs):
        labels.append(label)
        held.append(True)
        yield
        held.append(False)

    def runner(*args):
        assert held and held[-1] is True, "simulation outside the lock"
        return fake(*args)

    monkeypatch.setattr(model_run, "_run", runner)
    monkeypatch.setattr(heavy, "heavy_lock", fake_lock)
    monkeypatch.setattr(
        model_run,
        "freeze_record",
        lambda path: _clean_record({"policyengine-uk": "2.177.7"}),
    )
    model_run.build(
        dataset=dataset,
        allow_unmanaged=True,
        assemble=pipeline.assemble,
        runner=runner,
    )
    assert labels == ["uk-energy-price-cap-generate"]
    assert held == [True, False]
