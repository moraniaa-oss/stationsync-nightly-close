# StationSync Nightly Close — Meta Model API (Hackathon Build)

A fresh build of the StationSync nightly-close agent on Meta's hosted
models, made for the Meta Global AI Developer Hackathon. The production
agent runs every night on Al Morani's three live stores in Arkansas.
This project rebuilds the same job from scratch on the Meta Model API
to prove the workflow is portable to Muse Spark.

## What the demo does

Every night, a convenience store closes the same way. The crew counts
the drawer and writes a close sheet. The register prints its own
closing figures. The lottery terminal and the fuel totalizers keep
their own numbers. When those sources disagree, money is leaking and
nobody knows until weeks later.

The agent closes the store in five stages:

1. **Intake** — collects the night's material: crew close figures, the
   POS closing report, the lottery figures and the transaction journal.
2. **Extract** — reads the crew sheet and normalizes every figure into
   exact decimal money facts. In live mode, Muse Spark on the Meta
   Model API does the reading.
3. **Reconcile** — a script, never the model, cross-checks every figure
   against an independent source: departments vs POS sales, tenders vs
   everything rung, crew cash vs expected cash, card batch, lottery
   three ways, fuel. A night ties to the penny or names its difference.
4. **Fraud scan** — reads the journal for the patterns owners fear: a
   cash void that was never re-rung (flagged HIGH), no-sale drawer
   opens clustered in a quiet window (WATCH), and large cash sales
   sampled for receipt checks. Voids that were honestly re-rung are
   marked explained, so nobody chases a mistake.
5. **Report** — one plain readout for the owner: total rung, over or
   short, which checks tied, and every flag with its amount, cashier
   and time.

## Architecture

```text
fixtures/sample_night.json        (one night bundle: sheet, POS, journal)
        |
  nightly_close/intake.py         load + shape check
  nightly_close/extract.py        Decimal normalization (live: Muse Spark)
  nightly_close/reconcile.py      deterministic penny checks
  nightly_close/fraud_scan.py     deterministic journal rules
  nightly_close/report.py         owner readout
  nightly_close/agent.py          runs the five stages in order
  nightly_close/config.py         model, base URL, credential routes
run.py                            CLI entry point
```

Design rules carried over from production, on purpose:

- **Models read, scripts calculate.** The model never does arithmetic.
  Every money figure is a Python `Decimal` built from its string form,
  so reconciliation is exact to the penny, not approximately right.
- **Two sources or it did not happen.** No figure is trusted from one
  place. The crew sheet proves nothing until the POS agrees, and the
  POS proves nothing until the drawer count agrees.
- **A flag is not an accusation.** The scan separates HIGH flags from
  explained items and watch notes, exactly as the owner sees them in
  production.
- **Credentials never live in the project.** The API key sits in the
  registered Muse connector `custom.meta-model-api` and reaches a
  request as a surrogate that Muse swaps at send time. A
  `MODEL_API_KEY` environment variable is the documented fallback for
  standalone runs. See `~/workspace/custom-connectors/custom.meta-model-api/CONNECTOR.md`.

## How it maps to the production StationSync workflow

| Production (live, nightly) | This demo |
| --- | --- |
| Crew sends sheet photo, POS closing, lottery report to the store group | One JSON night bundle with the same three parts |
| Agent reads the sheet photo and the POS pull | Extract stage normalizes the bundle; live mode reads sheet text with Muse Spark |
| Close is booked into the store workbook, tied to the penny | Reconcile stage runs the same class of two-source penny checks |
| Fraud audit scans the day's journal per cashier | Fraud scan stage runs the same void and no-sale rules |
| Owner gets a signed nightly report | Report stage renders the same figures-first readout |

## Run it

Standard library only. No installs, no network in dry-run.

```bash
cd hackathon-build
python3 run.py                      # dry-run on the bundled sample night
python3 run.py --fixture other.json # dry-run on any other night bundle
```

Expected dry-run result on the bundled fixture: total rung $14,104.39,
over/short $0.00, 8 of 8 checks tied, and one HIGH flag — a planted
$86.40 cash void (transaction 1214, cashier 2, 21:47) that was never
re-rung.

## Dry-run is the default, live is locked

Live mode exists (`--live`) but refuses to run unless the environment
also sets `HACKATHON_LIVE=1`. That double guard is deliberate: the
$150 hackathon credits were claimed on Oct 26 2026 and land around
Wed Oct 28. Any live call before then would charge the owner's card.
Until credits land, this project spends exactly $0.00.

## Status

Scaffold built Oct 26 2026. Dry-run pipeline complete and verified.
Live phase (first real Muse Spark extraction, vision pass over sheet
photos, demo polish, submission packaging) is listed in BUILD-LOG.md.
Submission deadline: Wed Nov 4 2026, 8:00 PM CT.
