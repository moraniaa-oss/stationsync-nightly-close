#!/usr/bin/env python3
"""Run the StationSync nightly-close hackathon demo.

Usage:
  python3 run.py                      dry-run on the bundled sample night
  python3 run.py --fixture other.json dry-run on another night bundle
  python3 run.py --live               refused unless HACKATHON_LIVE=1

Dry-run is the default and makes no network calls. It proves the whole
pipeline end to end: intake, extract, reconcile to the penny, fraud
scan, owner report. Standard library only, no installs needed.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nightly_close import agent

DEFAULT_FIXTURE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "fixtures", "sample_night.json"
)


def main(argv=None):
    parser = argparse.ArgumentParser(description="StationSync nightly close, hackathon build")
    parser.add_argument("--fixture", default=DEFAULT_FIXTURE,
                        help="path to a night bundle JSON")
    parser.add_argument("--dry-run", action="store_true",
                        help="run the pipeline on fixtures with no network calls (default)")
    parser.add_argument("--live", action="store_true",
                        help="live mode, refused unless HACKATHON_LIVE=1 is set")
    args = parser.parse_args(argv)

    live = bool(args.live) and not args.dry_run
    result = agent.run(args.fixture, live_flag=live)
    print("Mode: %s (no network calls were made)" % result["mode"]
          if result["mode"] == "dry-run" else "Mode: live")
    print("")
    print(result["report"])

    failed = [c for c in result["checks"] if not c["ok"]]
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
