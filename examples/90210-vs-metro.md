# Worked example — ZIP 90210 vs Los Angeles metro FMR

```bash
python3 desk/quote.py --zip 90210 --br 2 --pct 110 --asking 4200
python3 desk/quote.py --compare 90210 --br 2
python3 desk/quote.py --county "Los Angeles" --state CA --br 2
```

Expected shape (FY2026 revised HUD tables):

- ZIP 90210 is in **Los Angeles-Long Beach-Glendale, CA HUD Metro FMR Area** (`METRO31080MM4480`).
- That metro is **mandatory SAFMR** (2023 designation, implemented 2025-01-01).
- 2BR SAFMR for 90210 is **$4,350**; 110% basic-range cap **$4,785**.
- Metro 2BR FMR is **$2,903**. Using the metro number in a mandatory SAFMR area understates the ZIP by **$1,447**.
- Asking **$4,200** is under 110% of the ZIP SAFMR and **over** 110% of the metro FMR ($3,193). A PHA still quoting off the metro table would wrongly treat $4,200 as an exception.

This is the product: ZIP vs metro, cited, offline.
