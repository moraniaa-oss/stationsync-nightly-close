"""Stage 5, report: the owner's morning readout.

Figures first, flags loud, no fluff. The owner reads this on a phone,
so the format is plain text with big clear lines. In production this
report carries the StationSync signature block. The demo build keeps
the same voice and marks itself as the hackathon demo.
"""

from .reconcile import over_short


def _fmt(amount):
    return "$%s" % format(amount, ",.2f")


def render(facts, checks, findings):
    """Build the owner report text from the pipeline results."""
    passed = sum(1 for c in checks if c["ok"])
    os_amount = over_short(checks)
    if os_amount == 0:
        os_line = "Over/short: $0.00, tied to the penny"
    else:
        os_line = "Over/short: %s, DOES NOT TIE" % _fmt(os_amount)

    lines = []
    lines.append("NIGHTLY CLOSE - %s" % facts["store_name"])
    lines.append("Business date: %s" % facts["business_date"])
    lines.append("Total rung: %s" % _fmt(facts["total_rung"]))
    lines.append(os_line)
    lines.append("")
    lines.append("RECONCILIATION: %d of %d checks tied" % (passed, len(checks)))
    for check in checks:
        mark = "OK  " if check["ok"] else "FAIL"
        lines.append("  [%s] %s" % (mark, check["name"]))
        if not check["ok"]:
            lines.append("       expected %s, got %s, difference %s"
                         % (_fmt(check["expected"]), _fmt(check["actual"]),
                            _fmt(check["difference"])))
    lines.append("")

    lines.append("FRAUD SCAN")
    if findings["flags"]:
        for flag in findings["flags"]:
            lines.append("  " + flag)
    else:
        lines.append("  No high flags.")
    for item in findings["explained"]:
        lines.append("  Explained: " + item)
    for item in findings["watch"]:
        lines.append("  " + item)
    for item in findings["info"]:
        lines.append("  Info: " + item)
    lines.append("")
    lines.append("- Powered by StationSync (hackathon demo build, Meta Model API)")
    return "\n".join(lines)
