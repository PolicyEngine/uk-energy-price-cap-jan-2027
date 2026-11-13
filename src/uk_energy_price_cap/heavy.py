"""The machine-wide heavy-run lock and memory gate.

A national run loads Microcosm and peaks at several GB, so only one heavy
job runs on the machine at a time. The protocol every repository on the
machine follows:

- the lock is a FILE, ``/tmp/pe-heavy.lock``, holding ``"<pid> <label>"``;
- it is created with noclobber (``O_CREAT | O_EXCL``), so a held lock, file
  or legacy directory, makes the caller wait;
- it is removed only by its owner: the process whose pid is its first field;
- once the lock is held, the run waits for 22 GB of free plus inactive
  memory (``vm_stat``, page size read from its header).

Tests pass a scratch ``path``; nothing here touches the real lock unless a
real national run asks for it.
"""

import os
import shutil
import signal
import subprocess
import threading
import time
from contextlib import contextmanager
from pathlib import Path

LOCK = Path("/tmp/pe-heavy.lock")
MIN_FREE_GB = 22.0


def free_inactive_gb() -> float | None:
    """vm_stat free plus inactive memory in GB (macOS), or None elsewhere."""
    if shutil.which("vm_stat") is None:
        return None
    out = subprocess.run(
        ["vm_stat"], capture_output=True, text=True, check=False
    ).stdout
    page = None
    pages = 0
    for line in out.splitlines():
        if "page size of" in line:
            page = int(line.split("page size of")[1].split()[0])
        if line.startswith(("Pages free:", "Pages inactive:")):
            pages += int(line.split(":")[1].strip().rstrip("."))
    if page is None:
        return None
    return pages * page / 1e9


def owner(path: Path = LOCK) -> str | None:
    """The pid field of the lock file, or None if there is no such file."""
    try:
        text = Path(path).read_text()
    except OSError:
        return None
    fields = text.split()
    return fields[0] if fields else None


def try_acquire(label: str, path: Path = LOCK) -> bool:
    """Create the lock with noclobber; False if any lock is already there."""
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    except FileExistsError:
        return False
    with os.fdopen(fd, "w") as handle:
        handle.write(f"{os.getpid()} {label}\n")
    return True


def release(path: Path = LOCK) -> bool:
    """Remove the lock only if this process owns it."""
    if owner(path) != str(os.getpid()):
        return False
    try:
        Path(path).unlink()
    except FileNotFoundError:
        return False
    return True


def _exit_on_term(signum, frame):
    raise SystemExit(128 + signum)


@contextmanager
def heavy_lock(
    label: str,
    path: Path | None = None,
    min_free_gb: float | None = None,
    poll: float = 15.0,
    mem_poll: float = 30.0,
    free_gb=free_inactive_gb,
):
    """Hold the heavy-run lock, after waiting for memory; release on exit.

    SIGTERM is turned into SystemExit while the lock is held, so a killed
    run still releases it. ``path`` and ``min_free_gb`` default to the
    module's ``LOCK`` and ``MIN_FREE_GB``, read at call time.
    """
    path = Path(LOCK if path is None else path)
    min_free_gb = MIN_FREE_GB if min_free_gb is None else min_free_gb
    while not try_acquire(label, path):
        time.sleep(poll)
    previous = None
    main = threading.current_thread() is threading.main_thread()
    if main:
        previous = signal.signal(signal.SIGTERM, _exit_on_term)
    try:
        while True:
            free = free_gb()
            if free is None or free >= min_free_gb:
                break
            time.sleep(mem_poll)
        yield
    finally:
        if main:
            signal.signal(signal.SIGTERM, previous)
        release(path)
