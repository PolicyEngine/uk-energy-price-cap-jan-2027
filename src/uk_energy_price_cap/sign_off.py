"""Whether publishing needs people's sign-off: one switch, on.

On (``REQUIRED = True``) while this repository is a pre-release template:
``publication.validate`` refuses a results file whose ``meta.placeholder``
is false, and refuses ``meta.placeholder`` false while any measure is still
a placeholder. Turn it off only in the G4 go-public commit, after two
people have checked the local production build (docs/RUNBOOK.md).
"""

REQUIRED = True
