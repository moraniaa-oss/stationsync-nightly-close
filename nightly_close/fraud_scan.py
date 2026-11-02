"""Stage 4, fraud scan: read the journal the way an owner would.

Three rules, all deterministic, all learned from real store nights:

1. A cash void that is never re-rung is a HIGH flag. A void erases a
   sale. When the same amount never comes back as a later sale, the
   money or the goods may have walked. This is the pattern behind the
   real repeat flags in production, so the scan leads with it.
2. A void that IS re-rung is explained, and the scan says so, so the
   owner does not chase honest mistakes.
3. Three or more no-sale drawer opens inside 15 minutes is a WATCH
   note. One no-sale is normal. A cluster at a quiet hour is worth an
   owner's glance, never an accusation.

Large cash sales are listed as information only, the sample an owner
would spot check against receipts.
"""

from decimal import Decimal

from .extract import money

LARGE_CASH = Decimal("100")
NO_SALE_WINDOW_MINUTES = 15
NO_SALE_CLUSTER = 3


def _minutes(hhmm):
    hours, mins = hhmm.split(":")
    return int(hours) * 60 + int(mins)


def _was_re_rung(journal, void_entry):
    """True when a later sale matches the voided amount exactly."""
    for entry in journal:
        if entry["id"] <= void_entry["id"]:
            continue
        if entry["type"] == "sale" and money(entry["amount"]) == money(void_entry["amount"]):
            return entry
    return None


def scan(journal):
    """Return flags, explained items and watch notes for one journal."""
    flags, explained, watch, info = [], [], [], []

    for entry in journal:
        if entry["type"] == "void":
            re_ring = _was_re_rung(journal, entry)
            if re_ring is not None:
                explained.append(
                    "Void %s ($%s, cashier %s) was re-rung as sale %s."
                    % (entry["id"], entry["amount"], entry["cashier"], re_ring["id"])
                )
            else:
                flags.append(
                    "HIGH: cash void %s ($%s, cashier %s, %s) was never re-rung. "
                    "No later sale matches it."
                    % (entry["id"], entry["amount"], entry["cashier"], entry["time"])
                )
        if entry["type"] == "sale" and entry.get("payment") == "cash":
            if money(entry["amount"]) >= LARGE_CASH:
                info.append(
                    "Large cash sale %s ($%s, cashier %s), receipt spot check sample."
                    % (entry["id"], entry["amount"], entry["cashier"])
                )

    no_sales = [e for e in journal if e["type"] == "no_sale"]
    for i, first in enumerate(no_sales):
        cluster = [
            e for e in no_sales[i:]
            if _minutes(e["time"]) - _minutes(first["time"]) <= NO_SALE_WINDOW_MINUTES
        ]
        if len(cluster) >= NO_SALE_CLUSTER:
            watch.append(
                "WATCH: %d no-sale drawer opens between %s and %s (cashier %s)."
                % (len(cluster), cluster[0]["time"], cluster[-1]["time"],
                   cluster[0]["cashier"])
            )
            break

    return {"flags": flags, "explained": explained, "watch": watch, "info": info}
