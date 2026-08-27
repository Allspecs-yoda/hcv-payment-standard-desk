# Sources — HCV Payment Standard Desk

Planning tool. Not a PHA determination, not legal advice.

## Primary tables (bundled)

| file | what | source | retrieved |
| --- | --- | --- | --- |
| `county_fmrs.csv` | 4,764 county/New England town rows; 0–4 BR FY2026 FMRs | HUD USER `FY26_FMRs_revised.xlsx` (sheet `FY26_FMRs_revised`) https://www.huduser.gov/portal/datasets/fmr/fmr2026/FY26_FMRs_revised.xlsx | 2026-08-27 |
| `zip_safmrs.csv.gz` | 51,895 ZIP×HUD-area rows; 0–4 BR FY2026 Small Area FMRs | HUD USER `fy2026_safmrs_revised.xlsx` https://www.huduser.gov/portal/datasets/fmr/fmr2026/fy2026_safmrs_revised.xlsx — listed on https://www.huduser.gov/portal/datasets/fmr/smallarea/index.html as **effective 2026-05-21** | 2026-08-27 |
| `mandatory_safmr.csv` | 65 HUD-designated mandatory SAFMR metros | HUD USER “Designated Small Area Fair Market Rent (SAFMR) Areas” PDF https://www.huduser.gov/portal/datasets/fmr/fmr2025/designated-safmr-areas.pdf | 2026-08-27 |
| `payment_rules.csv` | 90–110 basic range + exception paths | 24 CFR 982.503 (LII) https://www.law.cornell.edu/cfr/text/24/982.503 — [89 FR 38300, May 7, 2024] | 2026-08-27 |
| `hap_rules.csv` | HAP formula, family PS size rule, in-place decrease hold | 24 CFR 982.505 (LII) https://www.law.cornell.edu/cfr/text/24/982.505 — [89 FR 38302, May 7, 2024]; gross rent 24 CFR 982.4; TTP 24 CFR 5.628(a) | 2026-08-27 |

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

## HAP math (cited, not invented) — polish 2026-08-27T20:00Z

- HAP = lower of (payment standard − TTP) or (gross rent − TTP). 24 CFR 982.505(b).
- Gross rent = rent to owner + utility allowance. 24 CFR 982.4.
- Family payment standard = lower of voucher/family-unit-size PS and unit-size PS. 24 CFR 982.505(c)(1). Extra bedrooms on the lease do not raise subsidy.
- In-place decrease: PHA may keep the old family PS. If it cuts, the first reduction may not apply earlier than two years after the schedule decrease, and only after 12 months' written notice. 24 CFR 982.505(c)(3) as amended 89 FR 38302 (May 7, 2024).
- In-place increase: apply by the earliest of a gross-rent increase that would raise family share, first regular/interim reexam, or one year. 24 CFR 982.505(c)(4).
- TTP is the highest of 30% monthly adjusted income, 10% monthly income, welfare housing designation, or minimum rent. 24 CFR 5.628(a). `--mai` uses only the 30% prong as a planning proxy.
- Utility reimbursement is HAP above rent to owner. 24 CFR 982.4 / 982.514(b).
- Asking-rent vs payment standard remains a **planning** gap; HAP still needs a real TTP and a PHA Administrative Plan.

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
