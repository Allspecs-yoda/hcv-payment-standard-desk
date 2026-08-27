# Sources — HCV Payment Standard Desk

Planning tool. Not a PHA determination, not legal advice.

## Primary tables (bundled)

| file | what | source | retrieved |
| --- | --- | --- | --- |
| `county_fmrs.csv` | 4,764 county/New England town rows; 0–4 BR FY2026 FMRs | HUD USER `FY26_FMRs_revised.xlsx` (sheet `FY26_FMRs_revised`) https://www.huduser.gov/portal/datasets/fmr/fmr2026/FY26_FMRs_revised.xlsx | 2026-08-27 |
| `zip_safmrs.csv.gz` | 51,895 ZIP×HUD-area rows; 0–4 BR FY2026 Small Area FMRs | HUD USER `fy2026_safmrs_revised.xlsx` https://www.huduser.gov/portal/datasets/fmr/fmr2026/fy2026_safmrs_revised.xlsx — listed on https://www.huduser.gov/portal/datasets/fmr/smallarea/index.html as **effective 2026-05-21** | 2026-08-27 |
| `mandatory_safmr.csv` | 65 HUD-designated mandatory SAFMR metros | HUD USER “Designated Small Area Fair Market Rent (SAFMR) Areas” PDF https://www.huduser.gov/portal/datasets/fmr/fmr2025/designated-safmr-areas.pdf | 2026-08-27 |
| `payment_rules.csv` | 90–110 basic range + exception paths | 24 CFR 982.503 (LII) https://www.law.cornell.edu/cfr/text/24/982.503 — [89 FR 38300, May 7, 2024] | 2026-08-27 |

HUD USER FMR landing page: https://www.huduser.gov/portal/datasets/fmr.html

## Cleveland remap (do not invent)

The 2025 designated-areas PDF still lists **Cleveland-Elyria, OH MSA / METRO17460M17460**. FY2026 county + ZIP workbooks use **Cleveland, OH HUD Metro FMR Area / METRO17410N17460** (Cuyahoga County 2BR FMR $1,279). The desk maps the mandatory flag onto the FY2026 code. Original PDF code is cited, not copied as a live key.

## Payment-standard math (cited, not invented)

- Applicable FMR is ZIP SAFMR in designated metros or opt-in PHAs; else metro FMR or non-metro county FMR. 24 CFR 982.503(a)(1).
- Basic range = 90% up to 110% of the published applicable FMR. No HUD approval. 24 CFR 982.503(c).
- PHA must revise within 3 months of a new FMR if needed to stay in range. 24 CFR 982.503(c)(3).
- Non-SAFMR PHA may set a ZIP exception **up to 110% of that ZIP’s SAFMR** without HUD approval. Whole ZIP. 24 CFR 982.503(d)(2).
- 110–120% with HUD notification if success rate <75% or >40% of families pay >30% of adjusted income. 24 CFR 982.503(d)(3).
- Above 110% otherwise needs HUD approval + rental-market data. 24 CFR 982.503(d)(4).
- Reasonable accommodation: up to 120% without HUD approval; above 120% needs HUD. 24 CFR 982.503(d)(5).
- HUD also publishes 90%/110% columns in the SAFMR xlsx; the desk recomputes them with half-up rounding so county quotes match.

## Related (not bundled)

- 24 CFR 888.113 — FMR / SAFMR designation.
- PIH 2024-34 — consolidated HCV payment-standard guidance.
- FR-6426-N-01 / PIH 2023-32 — 41-metro expansion, implementation 2025-01-01 (notice said 2024-10-01; designated-areas PDF lists 2025-01-01 — desk uses the PDF date).
- 2016 SAFMR final rule — original 24 metros (Dallas court 2011 is extra).

## What this is not

- Not a substitute for a PHA Administrative Plan.
- Not PBV rent-to-owner (24 CFR 983.301).
- Not income limits / MTSP / HOME.
- Asking-rent vs payment standard is a **planning** gap, not a HAP calculation (982.505 uses the payment standard, family TTP, and gross rent).
