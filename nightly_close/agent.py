"""The agent core: run the five stages in order and print the report.

Stage map, mirroring the production StationSync close:
  intake     load and shape-check the night bundle
  extract    normalize every figure to Decimal money facts
  reconcile  script-side penny checks across independent sources
  fraud_scan journal rules (unre-rung voids, no-sale clusters)
  report     the owner's plain-language readout

Modes:
  dry-run  the default. Runs every stage on a bundled fixture and makes
           no network calls of any kind.
  live     needs --live AND HACKATHON_LIVE=1. Reserved for the phase
           after the user's credits land, when extract reads real crew
           sheet text through Muse Spark on the Meta Model API.
"""

from . import config, extract, fraud_scan, intake, reconcile, report


def run(bundle_path, live_flag=False):
    """Execute the pipeline for one night bundle. Returns a result dict."""
    if live_flag and not config.live_requested(live_flag):
        raise SystemExit(
            "Live mode refused: %s. Dry-run is the default until the "
            "hackathon credits land." % config.live_block_reason(live_flag)
        )

    bundle = intake.load_bundle(bundle_path)
    facts = extract.extract(bundle)
    checks = reconcile.reconcile(facts)
    findings = fraud_scan.scan(facts["journal"])
    text = report.render(facts, checks, findings)

    return {
        "facts": facts,
        "checks": checks,
        "findings": findings,
        "report": text,
        "mode": "live" if live_flag else "dry-run",
    }
