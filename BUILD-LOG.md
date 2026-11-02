# Build Log — StationSync Nightly Close, Meta Model API

## Oct 26 2026 — scaffold day (zero API spend)

### Built

- **Connector** `custom.meta-model-api` registered by the user and
  documented at `~/workspace/custom-connectors/custom.meta-model-api/`.
  Helper `bin/meta_model_api.py` (models list, one chat completion)
  written and compile checked. No live call has run yet.
- **Project scaffold** in this folder: `run.py` CLI plus the
  `nightly_close` package with five separated stages (intake, extract,
  reconcile, fraud_scan, report), an `agent.py` orchestrator and a
  `config.py` that holds the model name, the base URL
  `https://api.meta.ai/v1` and both credential routes (connector
  surrogate first, `MODEL_API_KEY` env fallback).
- **Sample fixture** `fixtures/sample_night.json`: one full night for a
  fictional but representative store — crew sheet, POS closing with six
  departments, lottery three ways, two fuel grades, and a seven-entry
  journal. One planted fraud pattern: an $86.40 cash void (Tran 1214)
  never re-rung, plus one honest void that was re-rung, a three-in-11-
  minutes no-sale cluster, and one large cash sale.
- **Live guard**: `--live` refuses unless `HACKATHON_LIVE=1` is also
  set. Verified: the refusal message prints and the run exits non-zero
  without any network call.

### Verified dry-run output (Oct 26 2026)

```text
Mode: dry-run (no network calls were made)
Total rung: $14,104.39
Over/short: $0.00, tied to the penny
RECONCILIATION: 8 of 8 checks tied
HIGH: cash void 1214 ($86.40, cashier 2, 21:47) was never re-rung.
Explained: Void 1103 ($24.10, cashier 1) was re-rung as sale 1104.
WATCH: 3 no-sale drawer opens between 20:03 and 20:14 (cashier 2).
```

All eight reconciliation checks tie exactly, and the fraud scan flags
only the planted discrepancy. Every module passes `py_compile`.

### Money spent today

$0.00. No live API call of any kind was made.

## Remaining — live phase

1. **First real API call** after the $150 credits land (expected Wed
   Oct 28 2026): run the connector helper `models` command as the
   harmless credential proof, then one `chat` call.
2. **Live extraction**: point `extract_live` at real crew sheet text
   from a sample night and confirm Muse Spark returns the fact shape
   the reconcile stage expects. Keep the script-calculates rule.
3. **Vision pass**: feed a sample close-sheet photo through Muse
   Spark image input (and SAM where it helps) so extraction starts
   from the photo, the way production intake does.
4. **Second and third store fixtures**: one liquor-store night and one
   fuel-heavy night, so the demo shows all three of the owner's store
   types, each with its own planted discrepancy.
5. **Demo script**: a five minute walkthrough — clean night ties, the
   planted void gets caught, owner report lands.
6. **Submission packaging** before Wed Nov 4 2026, 8:00 PM CT: repo
   tidy-up, README screenshots of a live run, final check that no
   production file, credential or store data ships in the package.

## Oct 26 2026 (evening) — fixtures 2 and 3 built (zero API spend)

- **liquor_night.json** — fictional liquor-store night (no fuel, small lottery): total rung $8,535.42, 7 of 8 checks tie; planted discrepancy is a drawer counted $12.50 short (the cash check FAILs by exactly -$12.50), one honestly re-rung void explained, no high flags.
- **fuel_night.json** — fictional fuel-heavy night (fuel $11,745.75 > merchandise $7,900.00, incl. diesel): total rung $21,967.12, cash ties to the penny, 7 of 8 checks tie; planted discrepancies are crew lottery instant sales $5.00 under POS (that one check FAILs) and a WATCH cluster of 4 no-sale drawer opens 02:07–02:18.
- Both verified with `python3 run.py --fixture ...` in dry-run; exit code 1 on each is expected — it is the runner signalling a named failed check, which is the demo point.
- Remaining live-phase item 4 is now DONE except the demo script. When the $150 credits land (~Wed Oct 28), the only blocking step left is the first live API call, then live extraction and the vision pass.

## Oct 26 2026 (night) — demo script written (zero API spend)

- **DEMO-SCRIPT.md** added: a timed five-minute walkthrough across all three fixtures (clean c-store night that still catches the $86.40 never-re-rung void; liquor night failing on exactly −$12.50 cash; fuel night failing on a $5.00 lottery miss plus a 02:07–02:18 no-sale watch), with exact run commands and presenter notes.
- All quoted figures re-verified by re-running the three fixtures in dry-run before writing (sample $14,104.39 / 8 of 8 / $0.00; liquor $8,535.42 / 7 of 8 / −$12.50; fuel $21,967.12 / 7 of 8, cash tied, lottery −$5.00).
- Live-phase item 5 (demo script) is now DONE. Remaining: first live API call, live extraction, vision pass, submission packaging — all gated on the credits landing ~Wed Oct 28.

## Scope lock — Al, Mon 2026-10-26 23:27 CDT
The hackathon build runs TONIGHT'S full client-agent design on the Meta Model API (Muse Spark), so costs are MEASURED, not estimated:
- Duties 1–9 as locked tonight: nightly close + penny reconciliation, per-cashier fraud scan, invoice intake → cost library, nightly increase logging, daily fuel briefing (public sources; DTN never), Thursday margin analysis → one recommendation list → owner-approves → execute (demo: mock POS batch), price changes on owner command.
- 15 owner commands/month in 3 sizes (small/medium/large) — each command type gets run and metered.
- EVERY run logs tokens + dollars per duty → the deliverable is a real per-store monthly cost sheet replacing the ~$64 API estimate.
- Duty 10 (Book Build) stays HELD — out of scope, pilot-only.
- IP-protection architecture is part of the demo story: agent runs server-side; clients receive outputs only.
- Production C Agent untouched. Live phase starts when the $150 credits land (~Wed Oct 28).
- A/B intake metering (added 2026-10-26 23:35): run the close fixture BOTH ways — photo-read vs form-fed (typed values) — and log cost + accuracy for each. First numbers on the forms question before anything is implemented in production. Also meter invoice intake three ways: WhatsApp-compressed photo vs email-original photo vs PDF text.

## 2026-10-30 ~11:48 AM CT — FIRST LIVE RUN ✅

- Al approved live API calls after verifying the $150 hackathon credits landed (dev.meta.ai billing: "Free credits in use $150.00").
- All three fixtures run LIVE (HACKATHON_LIVE=1, model muse-spark-1.1): sample_night exit 0 · liquor_night exit 1 · fuel_night exit 1 (exit 1 = the expected named failed check).
- Result: every DEMO-SCRIPT beat matched the dry-run figures exactly — sample tied 8/8 at $14,104.39 with the $86.40 never-re-rung void caught HIGH; liquor −$12.50 cash FAIL named; fuel lottery instant −$5.00 FAIL named. Zero figure differences from live extraction.
- Full outputs: ../../hidden_files/live-run-2026-10-30.md. No usage/cost figures printed by the runs.

## 2026-10-30 12:10 PM CT — VISION PASS ✅

- Crew sheet rendered as a paper-style photo (`fixtures/sample_sheet.png`, from the sample_night fixture) and read live by muse-spark-1.1 (OpenAI image_url format, first try — no fallback needed). New script: `vision_pass.py` (same HACKATHON_LIVE=1 guard; refuses with the env var unset, verified).
- **All 6 figures read exactly** — cash 4739.85 · card batch 7928.14 · lottery online 486.00 · instant 940.00 · cashes 612.00 · fuel totalizer 3653.58. Zero misreads.
- Vision-fed close **tied 8 of 8, over/short $0.00**, total rung $14,104.39, HIGH flag on the $86.40 never-re-rung void (cashier 2) intact. Photo intake is proven equivalent to the text path.
- Full output: ../../hidden_files/vision-pass-2026-10-30.md. No existing files were modified.
