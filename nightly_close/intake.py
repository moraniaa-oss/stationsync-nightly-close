"""Stage 1, intake: load one night's raw material and check its shape.

In production, intake is the crew sending the close sheet photo, the POS
closing figures and the lottery report into the store's group. In this
demo build, intake loads one JSON bundle with the same three parts:

- crew_sheet: what the crew counted by hand (cash, card batch, lottery)
- pos_closing: what the register printed at close (departments, tenders)
- journal: the day's transaction list, which the fraud scan reads

Intake validates only structure. It never judges the numbers. Judgment
belongs to reconcile and fraud_scan, so a bad figure fails loudly at the
stage that owns it.
"""

import json

REQUIRED_SECTIONS = ("store", "crew_sheet", "pos_closing", "journal")


def load_bundle(path):
    """Read a night bundle from disk and return it as a dict."""
    with open(path, "r", encoding="utf-8") as handle:
        bundle = json.load(handle)
    missing = [name for name in REQUIRED_SECTIONS if name not in bundle]
    if missing:
        raise ValueError("Night bundle is missing sections: " + ", ".join(missing))
    if not isinstance(bundle["journal"], list):
        raise ValueError("Night bundle journal must be a list of transactions")
    return bundle
