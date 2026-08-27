# HCV Payment Standard Desk

Offline FY2026 desk that prices a Housing Choice Voucher unit against **HUD Fair Market Rents** (4,764 county/town rows from `FY26_FMRs_revised.xlsx`) and **Small Area FMRs** (51,895 ZIP×area rows from `fy2026_safmrs_revised.xlsx`, effective 2026-05-21), flags the **65 mandatory SAFMR metros**, and prints the **90 / 110% basic range** in 24 CFR 982.503(c) — including the ZIP-exception path in 982.503(d)(2).

## Who it's for

PHA analysts, HCV landlords, housing navigators, and bid shops who still quote payment standards off a metro FMR in a mandatory SAFMR ZIP, treat 110% of the **wrong** FMR as the cap, or forget Cleveland’s FY2026 HUD area code is no longer `METRO17460M17460`.

## What's included

- `data/county_fmrs.csv` — 4,764 FY2026 0–4 BR FMRs (county + New England town)
- `data/zip_safmrs.csv.gz` — 51,895 ZIP SAFMRs (gunzip optional; the desk reads `.gz`)
- `data/mandatory_safmr.csv` — 65 designated metros (Dallas 2011 + 24 from 2016 + 41 from 2023)
- `data/payment_rules.csv` — 982.503(c)/(d)/(e) bands
- `data/sample_units.csv` — 12 asking-rent quotes
- `desk/quote.py` — `--zip`, `--county`, `--compare`, `--list-safmr`, `--batch`, `--watch`, `--cheap`, `--high`, `--rules`
- `examples/` — 90210 vs LA metro; 90/110 Birmingham
- `data/SOURCES.md` — HUD USER xlsx URLs + 24 CFR cites

## Quick start

```bash
python3 desk/quote.py --watch
python3 desk/quote.py --zip 90210 --br 2 --pct 110 --asking 4200
python3 desk/quote.py --compare 90210 --br 2
python3 desk/quote.py --county "Los Angeles" --state CA --br 2
python3 desk/quote.py --list-safmr
python3 desk/quote.py --batch data/sample_units.csv
python3 desk/quote.py --cheap 15
```

No API keys. No network after download.

## Price

$49 USD. Unlimited non-exclusive buyers; copies may be resold. Pay https://buy.stripe.com/00w4gAdW86UXaRQdQpcIE07 then open a GitHub issue titled `CLAIM: HCV Payment Standard Desk` with the receipt last-4. If checkout is down, star + watch and open the same CLAIM issue.

## License

MIT for the desk code. HUD FMR/SAFMR figures are U.S. government works; bundled CSVs are convenience extracts with source URLs in `data/SOURCES.md`.

## Foundry

Shipped by Night Shift Foundry for Dakota (@Allspecs-yoda).
SKU: NSF-20260827-HCV-PS | Decision: list | Cycle: 2026-08-27
