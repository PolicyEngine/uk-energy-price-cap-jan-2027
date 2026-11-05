"""Whether publishing needs people's sign-off: one switch, on.

On (``REQUIRED = True``) while this repository is a pre-release template:
nothing in ``dashboard/public/data`` may carry a measure that is not
``announced``, and ``publication.validate`` refuses a results file whose
``meta.placeholder`` is false while any placeholder remains. Turn it off
only at G4 on the day, after two people have checked the page behind the
login (docs/RUNBOOK.md).
"""

REQUIRED = True
