"""StationSync nightly-close agent, hackathon build on the Meta Model API.

A fresh, parallel implementation of the production StationSync close:
intake -> extract -> reconcile -> fraud scan -> owner report.

Dry-run is the default and makes no network calls. Live mode needs both
the --live flag and the HACKATHON_LIVE=1 environment variable.
"""

__all__ = ["config", "intake", "extract", "reconcile", "fraud_scan", "report", "agent"]
