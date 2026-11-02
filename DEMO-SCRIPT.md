# Demo Script — StationSync Nightly Close (Meta Model API build)

Five minutes, three store nights, one point: **the books close to the
penny, and the leaks get named the same night — not weeks later.**

Honest framing to open with, every time: this workflow already runs
in production every night on three real Arkansas stores. This build
re-creates it fresh on Meta's hosted models (Muse Spark via the Meta
Model API) to prove it is portable. No production data, no production
credentials, and no production system is touched by this demo.

All figures below are from verified dry runs on 2026-10-26. Beats
marked **[LIVE]** swap in once the $150 hackathon credits land
(~Wed Oct 28) — until then the same beats run in dry-run and spend
$0.00.

---

## Beat 1 — The problem (0:00–0:45)

Say: "Every night a store closes three different ways. The crew
counts the drawer and writes a sheet. The register prints its own
closing. The lottery terminal and the fuel pumps keep their own
numbers. When those disagree, money is leaking — and most owners
find out weeks later, if ever. StationSync closes all of it the
same night, to the penny."

Show: the three fixture nights on screen — a c-store, a liquor
store, a fuel-heavy store. Same close, three shapes of business.

## Beat 2 — The clean night that still catches something (0:45–2:00)

Run:

```bash
python3 run.py --fixture fixtures/sample_night.json
```

Say while it runs: "Five stages. Intake loads the night. Extract
turns the crew sheet into exact money facts — in live mode Muse
Spark does the reading. **[LIVE]** Then scripts — never the model —
do every calculation."

Point at the output, in order:

- **Total rung $14,104.39 · Over/short $0.00** — tied to the penny.
- **8 of 8 reconciliation checks tied** — departments, tenders,
  cash, cards, lottery three ways, fuel.
- Then the turn: **HIGH — cash void 1214, $86.40, cashier 2, 21:47,
  never re-rung.** "The night balances and *still* catches this.
  A void that is never re-rung is how money walks out of a drawer
  without the totals ever looking wrong."
- **Explained: void 1103 ($24.10) was re-rung as sale 1104.** "A
  flag is not an accusation — honest mistakes get marked explained
  so nobody chases them."
- **WATCH: 3 no-sale drawer opens, 20:03–20:14, cashier 2.** "Not
  proof of anything. A pattern the owner sees the same night."

## Beat 3 — The night that does not tie (2:00–3:15)

Run:

```bash
python3 run.py --fixture fixtures/liquor_night.json
```

Point at:

- **Total rung $8,535.42 · Over/short −$12.50 — DOES NOT TIE.**
- **7 of 8 checks tied; the one FAIL names itself:** crew cash
  count $2,894.49 vs expected $2,906.99, difference exactly
  **−$12.50**.

Say: "This is the other half of the product. When a night does not
tie, the owner does not get a vague 'something's off.' He gets the
one check that failed, the two numbers, and the exact difference —
small enough to find while the shift is still fresh in memory."

## Beat 4 — Fuel and lottery, the hard night (3:15–4:15)

Run:

```bash
python3 run.py --fixture fixtures/fuel_night.json
```

Point at:

- **Total rung $21,967.12** — fuel $11,745.75 is bigger than all
  merchandise combined; cash still ties to the penny.
- **The FAIL is lottery:** crew instant sales $1,180.00 vs POS
  $1,185.00 — **$5.00 under**, named to the check.
- **WATCH: 4 no-sale opens between 02:07 and 02:18** — the quiet
  hours, exactly when an owner is asleep.

Say: "Fuel and lottery are where c-store money actually leaks.
Both are reconciled here against independent sources, every night,
not sampled."

## Beat 5 — The rules and the close (4:15–5:00)

Say, plainly:

1. **Models read, scripts calculate.** The model never does
   arithmetic — every figure is an exact decimal, checked by code.
2. **Two sources or it didn't happen.** No number is trusted from
   one place; crew sheet, POS, terminal, and drawer must agree.
3. **This is not a mock-up of an idea.** The same workflow runs
   tonight, in production, on three live stores. This build proves
   it runs on Meta's models too.

Close: "StationSync — your books done by morning, to the penny,
with the leaks named."

---

## Presenter notes

- Dry-run is the default and spends nothing; live mode is double-
  guarded (`--live` plus `HACKATHON_LIVE=1`) so a rehearsal can
  never charge the owner's card before the credits land.
- Exit code 1 on the liquor and fuel nights is expected — it is
  the runner signalling a named failed check. That failure *is*
  the demo point; do not apologise for it.
- If asked "is the fraud real?": no — each fixture carries one
  planted discrepancy, labelled as such. The production system
  runs the same rules on real journals nightly.
- Submission deadline: Wed Nov 4 2026, 8:00 PM CT. Remaining after
  this script: first live Muse Spark call + live extraction,
  vision pass on a sheet photo, submission packaging — all gated
  on the credits landing ~Wed Oct 28.
