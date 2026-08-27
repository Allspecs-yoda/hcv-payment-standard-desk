#!/usr/bin/env python3
"""HCV Payment Standard Desk — offline FY2026 FMR / SAFMR quotes.

No network. No API keys. Planning only — not a PHA determination.

  python3 desk/quote.py --watch
  python3 desk/quote.py --zip 90210 --br 2
  python3 desk/quote.py --zip 90210 --br 2 --pct 110 --asking 4200
  python3 desk/quote.py --county "Los Angeles" --state CA --br 2
  python3 desk/quote.py --compare 90210 --br 2
  python3 desk/quote.py --list-safmr
  python3 desk/quote.py --list CA
  python3 desk/quote.py --batch data/sample_units.csv
  python3 desk/quote.py --cheap 15
  python3 desk/quote.py --high 10
  python3 desk/quote.py --hap 90210 --br 2 --vbr 2 --pct 110 --rent 4000 --ua 200 --ttp 1200
"""

from __future__ import annotations

import argparse
import csv
import gzip
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

BR_KEYS = {0: "fmr_0", 1: "fmr_1", 2: "fmr_2", 3: "fmr_3", 4: "fmr_4"}
SAFMR_KEYS = {0: "safmr_0", 1: "safmr_1", 2: "safmr_2", 3: "safmr_3", 4: "safmr_4"}


def hud_round(x: float) -> int:
    return int(x + 0.5) if x >= 0 else int(x - 0.5)


def money(n: float) -> str:
    return f"${int(round(n)):,}"


def load_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def zip_path() -> Path:
    gz = DATA / "zip_safmrs.csv.gz"
    raw = DATA / "zip_safmrs.csv"
    if gz.exists():
        return gz
    if raw.exists():
        return raw
    raise SystemExit("missing data/zip_safmrs.csv.gz")


def iter_zips():
    path = zip_path()
    if path.suffix == ".gz":
        f = gzip.open(path, "rt", encoding="utf-8", newline="")
    else:
        f = path.open(encoding="utf-8", newline="")
    with f:
        yield from csv.DictReader(f)


def counties() -> list[dict]:
    return load_csv(DATA / "county_fmrs.csv")


def mandatory() -> list[dict]:
    return load_csv(DATA / "mandatory_safmr.csv")


def rules() -> list[dict]:
    return load_csv(DATA / "payment_rules.csv")


def hap_rules() -> list[dict]:
    path = DATA / "hap_rules.csv"
    if not path.exists():
        return []
    return load_csv(path)


def mand_by_code() -> dict[str, dict]:
    return {r["hud_area_code"]: r for r in mandatory()}


def parse_int(s: str) -> int:
    return int(float(str(s).strip()))


def fmr_for_br(row: dict, br: int, kind: str) -> int:
    key = SAFMR_KEYS[br] if kind == "safmr" else BR_KEYS[br]
    return parse_int(row[key])


def ps(fmr: int, pct: int) -> int:
    return hud_round(fmr * pct / 100.0)


def find_zips(zipc: str) -> list[dict]:
    z = zipc.strip().zfill(5)
    hits = [r for r in iter_zips() if r["zip"] == z]
    if not hits:
        raise SystemExit(f"ZIP {z} is not in the FY2026 SAFMR table (metro ZIPs only).")
    return hits


def find_counties(needle: str, state: str | None) -> list[dict]:
    n = needle.strip().lower()
    st = state.upper() if state else None
    hits = []
    for r in counties():
        if st and r["stusps"] != st:
            continue
        name = r["countyname"].lower()
        town = (r["county_town_name"] or "").lower()
        area = r["hud_area_name"].lower()
        if n == name or n in name or n == town or n in town or n in area:
            hits.append(r)
    if not hits:
        raise SystemExit(f"No county matched {needle!r}" + (f" in {st}" if st else ""))
    return hits


def pick_county(hits: list[dict], needle: str) -> dict:
    n = needle.strip().lower()
    exact = [h for h in hits if h["countyname"].lower() == n or h["countyname"].lower() == n + " county"]
    if len(exact) == 1:
        return exact[0]
    if len(hits) == 1:
        return hits[0]
    names = ", ".join(f"{h['countyname']} {h['stusps']} ({h['hud_area_code']})" for h in hits[:12])
    raise SystemExit(f"Ambiguous. Matches: {names}. Pass --state or a tighter --county.")


_AREA_INDEX: dict[str, dict] | None = None


def area_fmr(code: str) -> dict | None:
    global _AREA_INDEX
    if _AREA_INDEX is None:
        idx: dict[str, dict] = {}
        for r in counties():
            idx.setdefault(r["hud_area_code"], r)
        _AREA_INDEX = idx
    return _AREA_INDEX.get(code)


def flag_mandatory(code: str) -> str:
    m = mand_by_code().get(code)
    if not m:
        return "metro_or_county_FMR (24 CFR 982.503(a)(1)(ii)/(iii))"
    return f"MANDATORY SAFMR ({m['cohort']}; impl {m['implemented']})"


def print_band(fmr: int, asking: int | None, pct: int) -> None:
    lo, mid, hi = ps(fmr, 90), ps(fmr, 100), ps(fmr, 110)
    print(f"  FMR: {money(fmr)}")
    print(f"  basic range 90/100/110: {money(lo)} / {money(mid)} / {money(hi)}")
    print(f"  payment standard at {pct}%: {money(ps(fmr, pct))}")
    if asking is not None:
        std = ps(fmr, pct)
        gap = asking - std
        if asking <= std:
            print(f"  asking {money(asking)} is AT OR UNDER the {pct}% standard (gap {money(std - asking)} headroom)")
        else:
            print(f"  asking {money(asking)} is OVER the {pct}% standard by {money(gap)}")
            need = (asking / fmr) * 100 if fmr else 0
            print(f"  asking is {need:.1f}% of FMR")
            if need > 110:
                print("  above 110% of applicable FMR needs a 982.503(d) exception path")


def cmd_zip(zipc: str, br: int, pct: int, asking: int | None) -> int:
    hits = find_zips(zipc)
    for i, row in enumerate(hits):
        if i:
            print("---")
        code = row["hud_area_code"]
        print(f"ZIP {row['zip']}  {br}BR")
        print(f"  area: {row['hud_area_name']} ({code})")
        print(f"  applicable FMR basis: {flag_mandatory(code)}")
        fmr = fmr_for_br(row, br, "safmr")
        print_band(fmr, asking, pct)
        metro = area_fmr(code)
        if metro:
            mf = fmr_for_br(metro, br, "fmr")
            print(f"  metro/county FMR {br}BR: {money(mf)} ({metro['hud_area_name']})")
            print(f"  ZIP vs metro: {money(fmr - mf)} ({((fmr / mf) - 1) * 100:+.1f}%)")
    if len(hits) > 1:
        print(f"\n{len(hits)} HUD areas share this ZIP. Quote each; do not blend.")
    print("Not a PHA payment-standard determination.")
    return 0


def cmd_county(needle: str, state: str | None, br: int, pct: int, asking: int | None) -> int:
    row = pick_county(find_counties(needle, state), needle)
    print(f"{row['countyname']} {row['stusps']}  {br}BR")
    print(f"  town: {row['county_town_name'] or '—'}")
    print(f"  area: {row['hud_area_name']} ({row['hud_area_code']})")
    print(f"  metro flag: {row['metro']}  pop2023: {row['pop2023']}")
    print(f"  applicable FMR basis: {flag_mandatory(row['hud_area_code'])}")
    fmr = fmr_for_br(row, br, "fmr")
    print_band(fmr, asking, pct)
    print("County FMR is the metro/non-metro published rent, not the ZIP SAFMR.")
    return 0


def cmd_compare(zipc: str, br: int) -> int:
    hits = find_zips(zipc)
    print(f"{'ZIP':<6} {'area':<44} {'SAFMR':>7} {'metro':>7} {'gap':>8} {'90':>7} {'110':>7} mand")
    for row in hits:
        code = row["hud_area_code"]
        sf = fmr_for_br(row, br, "safmr")
        metro = area_fmr(code)
        mf = fmr_for_br(metro, br, "fmr") if metro else 0
        mand = "YES" if code in mand_by_code() else "no"
        name = (row["hud_area_name"][:42] + "…") if len(row["hud_area_name"]) > 43 else row["hud_area_name"]
        print(
            f"{row['zip']:<6} {name:<44} {sf:>7} {mf:>7} {sf - mf:>+8} "
            f"{ps(sf, 90):>7} {ps(sf, 110):>7} {mand}"
        )
    print("Gap = ZIP SAFMR − metro/county FMR. Mandatory PHAs must use the ZIP column.")
    return 0


def cmd_list_safmr() -> int:
    rows = mandatory()
    print(f"{'code':<20} {'impl':<12} {'cohort':<14} area")
    for r in rows:
        print(f"{r['hud_area_code']:<20} {r['implemented']:<12} {r['cohort']:<14} {r['hud_area_name']}")
    print(f"\n{len(rows)} mandatory SAFMR metros (HUD USER designated-safmr-areas.pdf).")
    print("Cleveland FY2026 code is METRO17410N17460 (was METRO17460M17460 / Cleveland-Elyria).")
    return 0


def cmd_list_state(state: str | None) -> int:
    recs = counties()
    if state:
        recs = [r for r in recs if r["stusps"] == state.upper()]
        if not recs:
            print(f"unknown state {state}", file=sys.stderr)
            return 1
    print(f"{'ST':<3} {'county':<28} {'2BR':>6} {'area'}")
    shown = 0
    seen = set()
    for r in recs:
        key = (r["stusps"], r["countyname"], r["hud_area_code"])
        if key in seen:
            continue
        seen.add(key)
        print(f"{r['stusps']:<3} {r['countyname'][:28]:<28} {r['fmr_2']:>6} {r['hud_area_name']}")
        shown += 1
        if not state and shown >= 80:
            print("… truncated. Pass --list ST")
            break
    print(f"\n{shown} rows. County table has {len(counties())} FIPS/town lines.")
    return 0


def cmd_batch(path: Path, pct_default: int) -> int:
    recs = load_csv(path)
    print(f"{'id':<14} {'zip':<6} {'br':>2} {'ask':>7} {'SAFMR':>7} {'PS':>7} {'vs PS':>8} mand")
    over = 0
    for rec in recs:
        zipc = rec["zip"].zfill(5)
        br = int(rec["br"])
        asking = int(float(rec["asking_rent"]))
        pct = int(rec["pct"]) if rec.get("pct") else pct_default
        try:
            hits = find_zips(zipc)
        except SystemExit:
            print(f"{rec.get('id',''):<14} {zipc:<6} ZIP not in SAFMR table")
            continue
        row = hits[0]
        sf = fmr_for_br(row, br, "safmr")
        std = ps(sf, pct)
        gap = asking - std
        if gap > 0:
            over += 1
        mand = "Y" if row["hud_area_code"] in mand_by_code() else "n"
        sign = "+" if gap > 0 else ""
        print(
            f"{rec.get('id',''):<14} {zipc:<6} {br:>2} {money(asking):>7} {money(sf):>7} "
            f"{money(std):>7} {sign}{money(gap):>7} {mand}"
        )
        if len(hits) > 1:
            print(f"  note: {len(hits)} HUD areas for this ZIP; used {row['hud_area_name']}")
    print(f"\n{over}/{len(recs)} asking rents sit over the chosen % of ZIP SAFMR.")
    return 0


def cmd_watch() -> int:
    print("FY2026 HCV payment-standard watches (not the whole table):")
    print("- Applicable FMR is ZIP SAFMR in 65 designated metros (24 CFR 982.503(a)(1)(i) + 888.113(c)(1)).")
    print("- Basic range is 90–110% of that applicable FMR with no HUD approval (982.503(c)).")
    print("- Non-SAFMR PHAs may still set a ZIP exception up to 110% of that ZIP's SAFMR (982.503(d)(2)).")
    print("- 110–120% needs HUD notification if success-rate or rent-burden tests hit (982.503(d)(3)).")
    print("- Reasonable accommodation: 120% without HUD approval; above 120% needs HUD (982.503(d)(5)).")
    print("- FY2026 FMRs: HUD USER FY26_FMRs_revised.xlsx (effective with the FY2026 schedule).")
    print("- FY2026 SAFMRs revised file effective 2026-05-21 (huduser smallarea index).")
    print("- Cleveland FY2026 HUD area code remapped METRO17460M17460 → METRO17410N17460.")
    print("- HAP = lower of (PS − TTP) or (gross rent − TTP); 24 CFR 982.505(b). Gross rent = rent to owner + UA (982.4).")
    print("- Family PS = lower of voucher-size PS and unit-size PS (982.505(c)(1)). Extra bedrooms do not raise subsidy.")
    print("- In-place PS decrease: first cut not earlier than two years + 12 months' notice (982.505(c)(3); 89 FR 38302).")
    print("- TTP planning proxy: 30% of monthly adjusted income is only one 5.628(a) prong — pass --ttp when known.")
    print()
    cmd_list_safmr()
    return 0


def cmd_cheap(n: int) -> int:
    """ZIPs where SAFMR 2BR is furthest ABOVE metro FMR — opportunity / exception fuel."""
    mand = mand_by_code()
    scored: list[tuple[int, dict, int, int]] = []
    for row in iter_zips():
        metro = area_fmr(row["hud_area_code"])
        if not metro:
            continue
        sf = parse_int(row["safmr_2"])
        mf = parse_int(metro["fmr_2"])
        if mf <= 0:
            continue
        scored.append((sf - mf, row, sf, mf))
    scored.sort(key=lambda t: t[0], reverse=True)
    print(f"Top {n} ZIP 2BR SAFMRs above their metro FMR (exception / opportunity signal)\n")
    print(f"{'ZIP':<6} {'gap':>7} {'SAFMR':>7} {'metro':>7} {'110 ZIP':>8} mand area")
    for gap, row, sf, mf in scored[:n]:
        m = "Y" if row["hud_area_code"] in mand else "n"
        print(
            f"{row['zip']:<6} {money(gap):>7} {money(sf):>7} {money(mf):>7} "
            f"{money(ps(sf, 110)):>8} {m} {row['hud_area_name'][:40]}"
        )
    return 0


def cmd_high(n: int) -> int:
    rows = []
    for row in iter_zips():
        rows.append((parse_int(row["safmr_2"]), row))
    rows.sort(key=lambda t: t[0], reverse=True)
    print(f"Highest {n} ZIP 2BR SAFMRs, FY2026 revised\n")
    print(f"{'ZIP':<6} {'2BR':>7} {'110%':>8} area")
    for sf, row in rows[:n]:
        print(f"{row['zip']:<6} {money(sf):>7} {money(ps(sf, 110)):>8} {row['hud_area_name']}")
    return 0


def cmd_rules() -> int:
    print(f"{'id':<16} {'band':<12} {'HUD':<14} authority")
    for r in rules():
        band = f"{r['low_pct']}-{r['high_pct']}%"
        print(f"{r['rule_id']:<16} {band:<12} {r['hud_approval']:<14} {r['authority']}")
        print(f"  {r['notes']}")
    rows = hap_rules()
    if rows:
        print("\n982.505 HAP rules")
        for r in rows:
            print(f"{r['rule_id']:<16} {r['authority']}")
            print(f"  {r['notes']}")
    return 0


def ttp_from_args(ttp: int | None, mai: int | None) -> int:
    if ttp is not None:
        return ttp
    if mai is not None:
        return hud_round(0.30 * mai)
    raise SystemExit("HAP quote needs --ttp (known TTP) or --mai (monthly adjusted income; 5.628(a)(1) 30% prong only).")


def family_payment_standard(ps_voucher: int, ps_unit: int, hold_old: int | None, years_in_unit: float | None) -> tuple[int, str]:
    base = min(ps_voucher, ps_unit)
    note = "982.505(c)(1) lower of voucher-size PS and unit-size PS"
    if hold_old is None:
        return base, note
    if years_in_unit is None:
        raise SystemExit("--hold-old needs --years-in-unit (years the family has stayed in this unit since the schedule decrease).")
    if hold_old <= base:
        return base, note + "; --hold-old is not above the current schedule"
    if years_in_unit < 2:
        return hold_old, (
            "982.505(c)(3): in-place decrease may not apply earlier than two years after the "
            f"schedule drop (family in unit {years_in_unit:g}y); quoting hold-old PS {hold_old}"
        )
    return base, (
        "982.505(c)(3): two-year floor elapsed; quoting current schedule. "
        "Still needs 12 months' written notice before a cut hits the family."
    )


def print_hap(
    zipc: str,
    row: dict,
    unit_br: int,
    voucher_br: int,
    pct: int,
    rent: int,
    ua: int,
    ttp: int,
    hold_old: int | None,
    years_in_unit: float | None,
) -> None:
    code = row["hud_area_code"]
    fmr_unit = fmr_for_br(row, unit_br, "safmr")
    fmr_vouch = fmr_for_br(row, voucher_br, "safmr")
    ps_unit = ps(fmr_unit, pct)
    ps_vouch = ps(fmr_vouch, pct)
    fam_ps, ps_note = family_payment_standard(ps_vouch, ps_unit, hold_old, years_in_unit)
    gross = rent + ua
    hap = max(0, min(fam_ps - ttp, gross - ttp))
    family_share = gross - hap
    family_rent = max(0, rent - hap)
    ureimb = max(0, hap - rent)
    cap = "payment standard" if (fam_ps - ttp) <= (gross - ttp) else "gross rent"
    print(f"ZIP {row['zip']}  unit {unit_br}BR  voucher {voucher_br}BR  {pct}%")
    print(f"  area: {row['hud_area_name']} ({code})")
    print(f"  applicable FMR basis: {flag_mandatory(code)}")
    print(f"  unit SAFMR / PS: {money(fmr_unit)} / {money(ps_unit)}")
    print(f"  voucher SAFMR / PS: {money(fmr_vouch)} / {money(ps_vouch)}")
    print(f"  family payment standard: {money(fam_ps)}  ({ps_note})")
    print(f"  rent to owner {money(rent)} + UA {money(ua)} = gross rent {money(gross)}  (982.4)")
    print(f"  TTP: {money(ttp)}")
    print(f"  PS−TTP {money(fam_ps - ttp)} vs gross−TTP {money(gross - ttp)} → HAP {money(hap)} (capped by {cap}; 982.505(b))")
    print(f"  family share: {money(family_share)}  family rent to owner: {money(family_rent)}  utility reimbursement: {money(ureimb)}")
    if voucher_br != unit_br:
        print("  (c)(1) used the lower bedroom column — extra bedrooms on the lease do not raise the family PS.")
    if ttp > fam_ps:
        print("  TTP exceeds family PS; HAP is $0 (planning).")
    print("  Not a HAP determination. TTP here is an input, not a 5.628 highest-of computation unless --mai.")


def cmd_hap(
    zipc: str,
    unit_br: int,
    voucher_br: int,
    pct: int,
    rent: int | None,
    ua: int,
    ttp: int | None,
    mai: int | None,
    hold_old: int | None,
    years_in_unit: float | None,
) -> int:
    if rent is None:
        raise SystemExit("--hap needs --rent (rent to owner, 982.4).")
    ttp_val = ttp_from_args(ttp, mai)
    hits = find_zips(zipc)
    for i, row in enumerate(hits):
        if i:
            print("---")
        print_hap(zipc, row, unit_br, voucher_br, pct, rent, ua, ttp_val, hold_old, years_in_unit)
    if len(hits) > 1:
        print(f"\n{len(hits)} HUD areas share this ZIP. Quote each; do not blend.")
    return 0


def cmd_hap_batch(path: Path) -> int:
    recs = load_csv(path)
    print(f"{'id':<18} {'zip':<6} {'u/v':<4} {'gross':>7} {'PS':>7} {'TTP':>6} {'HAP':>7} cap")
    for rec in recs:
        zipc = rec["zip"].zfill(5)
        unit_br = int(rec["br"])
        voucher_br = int(rec["vbr"]) if rec.get("vbr") else unit_br
        pct = int(rec["pct"]) if rec.get("pct") else 110
        rent = int(float(rec["rent_to_owner"]))
        ua = int(float(rec.get("utility_allowance") or 0))
        ttp = int(float(rec["ttp"]))
        try:
            hits = find_zips(zipc)
        except SystemExit:
            print(f"{rec.get('id',''):<18} {zipc:<6} ZIP not in SAFMR table")
            continue
        row = hits[0]
        fmr_unit = fmr_for_br(row, unit_br, "safmr")
        fmr_vouch = fmr_for_br(row, voucher_br, "safmr")
        fam_ps = min(ps(fmr_vouch, pct), ps(fmr_unit, pct))
        gross = rent + ua
        hap = max(0, min(fam_ps - ttp, gross - ttp))
        cap = "PS" if (fam_ps - ttp) <= (gross - ttp) else "GR"
        print(
            f"{rec.get('id',''):<18} {zipc:<6} {unit_br}/{voucher_br:<3} {money(gross):>7} "
            f"{money(fam_ps):>7} {money(ttp):>6} {money(hap):>7} {cap}"
        )
    print("HAP = max(0, min(PS−TTP, gross−TTP)) per 982.505(b). Planning only.")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="FY2026 HCV payment-standard desk (offline)")
    p.add_argument("--zip", dest="zipc", help="5-digit ZIP (SAFMR)")
    p.add_argument("--county", help="county or New England town")
    p.add_argument("--state", help="ST")
    p.add_argument("--br", type=int, default=2, help="bedrooms 0-4 (default 2)")
    p.add_argument("--pct", type=int, default=110, help="payment standard % of FMR (default 110)")
    p.add_argument("--asking", type=int, help="asking rent USD")
    p.add_argument("--compare", metavar="ZIP", help="ZIP SAFMR vs metro FMR")
    p.add_argument("--list-safmr", action="store_true")
    p.add_argument("--list", nargs="?", const="", metavar="ST")
    p.add_argument("--batch", help="CSV of sample units")
    p.add_argument("--watch", action="store_true")
    p.add_argument("--cheap", type=int, nargs="?", const=15, metavar="N")
    p.add_argument("--high", type=int, nargs="?", const=10, metavar="N")
    p.add_argument("--rules", action="store_true")
    p.add_argument("--hap", metavar="ZIP", help="982.505 HAP quote for a ZIP (needs --rent and --ttp or --mai)")
    p.add_argument("--vbr", type=int, help="voucher / family unit size bedrooms (default: --br)")
    p.add_argument("--rent", type=int, help="rent to owner USD (982.4)")
    p.add_argument("--ua", type=int, default=0, help="utility allowance USD (default 0)")
    p.add_argument("--ttp", type=int, help="known total tenant payment USD")
    p.add_argument("--mai", type=int, help="monthly adjusted income USD; TTP = 30% (5.628(a)(1) only)")
    p.add_argument("--hold-old", type=int, dest="hold_old", help="prior in-place family PS for 982.505(c)(3) hold")
    p.add_argument("--years-in-unit", type=float, dest="years_in_unit", help="years family has stayed since the PS decrease")
    p.add_argument("--hap-batch", dest="hap_batch", help="CSV of HAP sample units")
    args = p.parse_args()
    if args.br not in BR_KEYS:
        print("--br must be 0..4", file=sys.stderr)
        return 1
    if args.pct < 0:
        print("--pct must be >= 0", file=sys.stderr)
        return 1
    if args.watch:
        return cmd_watch()
    if args.list_safmr:
        return cmd_list_safmr()
    if args.rules:
        return cmd_rules()
    if args.hap_batch:
        return cmd_hap_batch(Path(args.hap_batch))
    if args.hap:
        vbr = args.vbr if args.vbr is not None else args.br
        if vbr not in BR_KEYS:
            print("--vbr must be 0..4", file=sys.stderr)
            return 1
        return cmd_hap(
            args.hap,
            args.br,
            vbr,
            args.pct,
            args.rent,
            args.ua,
            args.ttp,
            args.mai,
            args.hold_old,
            args.years_in_unit,
        )
    if args.list is not None:
        return cmd_list_state(args.list or None)
    if args.compare:
        return cmd_compare(args.compare, args.br)
    if args.batch:
        return cmd_batch(Path(args.batch), args.pct)
    if args.cheap is not None:
        return cmd_cheap(args.cheap)
    if args.high is not None:
        return cmd_high(args.high)
    if args.zipc:
        return cmd_zip(args.zipc, args.br, args.pct, args.asking)
    if args.county:
        return cmd_county(args.county, args.state, args.br, args.pct, args.asking)
    p.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
