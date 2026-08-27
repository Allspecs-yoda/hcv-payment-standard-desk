# Worked example — 90 / 110 basic range

24 CFR 982.503(c): a basic-range payment standard is any dollar amount from **90% up to 110%** of the published applicable FMR. No HUD approval.

```bash
python3 desk/quote.py --rules
python3 desk/quote.py --zip 35203 --br 2 --pct 90 --asking 1100
python3 desk/quote.py --zip 35203 --br 2 --pct 110 --asking 1100
```

Birmingham-Hoover (`METRO13820M13820`) is mandatory SAFMR (expansion 41, 2025-01-01). ZIP 35203 2BR SAFMR **$1,020**.

- 90% = $918
- 110% = $1,122
- Asking $1,100 is over 90% and under 110% — in range at 110%, out of range at 90%.

Non-SAFMR PHAs can still lift a single ZIP to **110% of that ZIP’s SAFMR** under 982.503(d)(2) without HUD approval. That is not the same as opting into SAFMRs for the whole jurisdiction.
