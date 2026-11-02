"""Stage 3, reconcile: the script does the arithmetic, never the model.

This is the production StationSync rule, kept on purpose: models read,
scripts calculate. Every check compares two independent sources of the
same figure, in Decimal, and passes only when the difference is exactly
zero. A close that ties to the penny says so. A close that does not tie
names the check and the exact difference.
"""

from decimal import Decimal

ZERO = Decimal("0")


def _check(name, expected, actual):
    diff = actual - expected
    return {
        "name": name,
        "expected": expected,
        "actual": actual,
        "difference": diff,
        "ok": diff == ZERO,
    }


def reconcile(facts):
    """Run every penny check and return the list of results."""
    dept_sum = sum(facts["departments"].values(), ZERO)
    tenders = facts["tender_card"] + facts["tender_ebt"] + facts["tender_cash"]
    # Lottery cashes are money paid OUT of the drawer during the day, so
    # they sit on the rung side of the ledger, not the tender side.
    expected_cash = facts["tender_cash"] - facts["lottery_cashes_pos"]

    checks = [
        _check("Department sales add up to POS merchandise sales",
               facts["merchandise_sales"], dept_sum),
        _check("Tenders plus lottery cashes equal everything rung",
               facts["total_rung"], tenders + facts["lottery_cashes_pos"]),
        _check("Crew cash count equals expected cash in drawer",
               expected_cash, facts["crew_cash_counted"]),
        _check("Crew card batch equals POS card tender",
               facts["tender_card"], facts["crew_card_batch"]),
        _check("Lottery online sales, crew vs POS",
               facts["lottery_online_pos"], facts["crew_lottery_online"]),
        _check("Lottery instant sales, crew vs POS",
               facts["lottery_instant_pos"], facts["crew_lottery_instant"]),
        _check("Lottery cashes, crew vs POS",
               facts["lottery_cashes_pos"], facts["crew_lottery_cashes"]),
        _check("Fuel dollars, crew totalizer vs POS",
               facts["fuel_dollars_pos"], facts["crew_fuel_totalizer"]),
    ]
    return checks


def over_short(checks):
    """The cash over or short for the night, from the cash check."""
    for check in checks:
        if check["name"].startswith("Crew cash count"):
            return check["difference"]
    return ZERO
