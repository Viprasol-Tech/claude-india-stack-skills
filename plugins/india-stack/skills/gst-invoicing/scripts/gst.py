#!/usr/bin/env python3
"""GST invoice maths: CGST+SGST / CGST+UTGST / IGST split, rounding, invoice
number checks, Indian number formatting and amount in words.

Part of claude-india-stack-skills by Viprasol Tech Private Limited.

Tax type follows the supplier's state and the place of supply (the IGST Act
decides place of supply - this script takes it as an input). Amounts are
Decimal, computed to paise; the invoice total can be rounded to the rupee with
the difference shown as round-off (as the e-invoice RndOffAmt field allows).
Standard library only. Run ``python gst.py --self-test`` to check it.

  python gst.py calc --supplier-state 27 --pos 27 --item "Laptop,1,52000,18" --item "Mouse,2,499.50,18"
  python gst.py calc --supplier-state 27 --pos 29 --item "Consulting,1,100000,18" --round-total
  python gst.py invoice-no INV/2026-27/0001
  python gst.py words 125000.50
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import inr  # noqa: E402

PAISE = Decimal("0.01")
# Union territories without a legislature charge UTGST instead of SGST.
UTGST_CODES = {"04", "25", "26", "31", "35", "38", "97"}
MAX_AMOUNT = Decimal("1e15")
STATE_CODES = {f"{i:02d}" for i in range(1, 39)} | {"96", "97", "99"}
RULE46_RE = re.compile(r"^[A-Za-z0-9/-]{1,16}$")
EINVOICE_NO_RE = re.compile(r"^[A-Z1-9][A-Z0-9/-]{0,15}$")


def money(value: str | Decimal) -> Decimal:
    try:
        d = Decimal(str(value).strip())
    except InvalidOperation as exc:
        raise ValueError(f"not an amount: {value!r}") from exc
    if not d.is_finite() or abs(d) >= MAX_AMOUNT:
        raise ValueError(f"not a supported amount: {value!r}")
    return d


def tax_kind(supplier_state: str, place_of_supply: str, export_or_sez: bool = False) -> str:
    for code in (supplier_state, place_of_supply):
        if code not in STATE_CODES:
            raise ValueError(f"unknown GST state code {code!r}")
    if export_or_sez or place_of_supply == "96" or supplier_state != place_of_supply:
        return "IGST"
    return "CGST+UTGST" if supplier_state in UTGST_CODES else "CGST+SGST"


def calc(items: list[dict], supplier_state: str, place_of_supply: str,
         export_or_sez: bool = False, round_total: bool = False, lut: bool = False) -> dict:
    """lut=True: zero-rated export/SEZ supply under a Letter of Undertaking (IGST Act s.16) - IGST 0."""
    kind = tax_kind(supplier_state, place_of_supply, export_or_sez)
    if lut and not (export_or_sez or place_of_supply == "96"):
        raise ValueError("--lut applies only to exports and SEZ supplies")
    lines, taxable_sum, tax_sum = [], Decimal(0), {"CGST": Decimal(0), "SGST": Decimal(0), "UTGST": Decimal(0), "IGST": Decimal(0)}
    for it in items:
        if not isinstance(it, dict):
            raise ValueError(f"each item must be an object, got {it!r}")
        qty, price, rate = money(it["qty"]), money(it["unit_price"]), money(it["rate"])
        if lut:
            rate = Decimal(0)
        discount = money(it.get("discount", "0"))
        if qty <= 0 or price < 0 or rate < 0 or discount < 0:
            raise ValueError(f"invalid line: {it}")
        taxable = (qty * price - discount).quantize(PAISE, rounding=ROUND_HALF_UP)
        if taxable < 0:
            raise ValueError(f"discount exceeds line value: {it}")
        line = {"description": it.get("description", ""), "qty": str(qty), "unit_price": str(price),
                "taxable_value": taxable, "rate": str(rate)}
        if kind == "IGST":
            line["IGST"] = (taxable * rate / 100).quantize(PAISE, rounding=ROUND_HALF_UP)
        else:
            half = (taxable * rate / 200).quantize(PAISE, rounding=ROUND_HALF_UP)
            state_tax = "UTGST" if kind == "CGST+UTGST" else "SGST"
            line["CGST"], line[state_tax] = half, half  # equal halves, each rounded once
        line["total"] = taxable + sum(line.get(k, Decimal(0)) for k in tax_sum)
        for k in tax_sum:
            tax_sum[k] += line.get(k, Decimal(0))
        taxable_sum += taxable
        lines.append(line)
    gross = taxable_sum + sum(tax_sum.values())
    rounded = gross.quantize(Decimal(1), rounding=ROUND_HALF_UP) if round_total else gross
    return {
        "tax_type": kind,
        "supplier_state": supplier_state,
        "place_of_supply": place_of_supply,
        "lines": lines,
        "taxable_value": taxable_sum,
        "taxes": {k: v for k, v in tax_sum.items() if v or k in kind},
        "round_off": rounded - gross,
        "invoice_total": rounded,
        "amount_in_words": inr.amount_in_words(rounded),
        "note": ("Supply meant for export / SEZ unit or developer under LUT without payment of IGST"
                 if lut else ""),
    }


def check_invoice_no(no: str) -> dict:
    """CGST Rule 46: up to 16 characters, letters, digits, '-' and '/', unique per financial year.
    The e-invoice schema is stricter: uppercase only, and no leading 0, '/' or '-'."""
    errs = []
    if not RULE46_RE.match(no):
        errs.append("Rule 46: max 16 characters; only letters, digits, '-' and '/'")
    einv = bool(EINVOICE_NO_RE.match(no))
    return {"invoice_no": no, "rule46_ok": not errs, "einvoice_ok": einv and not errs, "errors": errs,
            "note": "must be consecutive and unique within the financial year" if not errs else ""}


def _jsonable(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError


def _self_test() -> None:
    inr.self_test()
    assert tax_kind("27", "27") == "CGST+SGST" and tax_kind("27", "29") == "IGST"
    assert tax_kind("04", "04") == "CGST+UTGST" and tax_kind("27", "27", export_or_sez=True) == "IGST"
    assert tax_kind("29", "96") == "IGST"
    try:
        tax_kind("27", "28x")
    except ValueError:
        pass
    else:
        raise AssertionError("bad code accepted")
    r = calc([{"qty": "1", "unit_price": "52000", "rate": "18"},
              {"qty": "2", "unit_price": "499.50", "rate": "18"}], "27", "27")
    assert r["taxable_value"] == Decimal("52999.00")
    assert r["taxes"]["CGST"] == r["taxes"]["SGST"] == Decimal("4769.91")
    assert r["invoice_total"] == Decimal("62538.82"), r["invoice_total"]
    r2 = calc([{"qty": "1", "unit_price": "999.99", "rate": "18"}], "27", "29", round_total=True)
    assert r2["taxes"]["IGST"] == Decimal("180.00") and r2["invoice_total"] == Decimal("1180")
    assert r2["round_off"] == Decimal("0.01") and r2["amount_in_words"] == "Rupees One Thousand One Hundred Eighty Only"
    r3 = calc([{"qty": "3", "unit_price": "33.33", "rate": "5", "discount": "10"}], "07", "07")
    assert r3["lines"][0]["taxable_value"] == Decimal("89.99") and r3["taxes"]["CGST"] == Decimal("2.25")
    z = calc([{"qty": "1", "unit_price": "1000", "rate": "18"}], "27", "96", lut=True)
    assert z["taxes"]["IGST"] == Decimal("0") and z["invoice_total"] == Decimal("1000.00") and "LUT" in z["note"]
    paid = calc([{"qty": "1", "unit_price": "1000", "rate": "18"}], "27", "96")
    assert paid["taxes"]["IGST"] == Decimal("180.00")  # export with payment of IGST (refund route)
    for bad in (lambda: calc([{"qty": "1", "unit_price": "1", "rate": "18"}], "27", "29", lut=True),
                lambda: money("1e30"), lambda: calc(["x"], "27", "27")):
        try:
            bad()
        except ValueError:
            pass
        else:
            raise AssertionError("must reject")
    assert tax_kind("97", "97") == "CGST+UTGST"
    ok = check_invoice_no("INV/2026-27/0001")
    assert ok["rule46_ok"] and ok["einvoice_ok"]
    assert not check_invoice_no("INV/2026-27/000001")["rule46_ok"]        # 18 chars
    assert check_invoice_no("inv-1")["rule46_ok"] and not check_invoice_no("inv-1")["einvoice_ok"]
    assert not check_invoice_no("0001")["einvoice_ok"] and not check_invoice_no("A#1")["rule46_ok"]
    print("gst self-test passed")


def _parse_item(text: str) -> dict:
    parts = [p.strip() for p in text.split(",")]
    if len(parts) not in (4, 5):
        raise ValueError(f"--item expects 'description,qty,unit_price,rate[,discount]', got {text!r}")
    keys = ["description", "qty", "unit_price", "rate", "discount"]
    return dict(zip(keys, parts))


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="GST invoice maths")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    c = sub.add_parser("calc", help="Compute an invoice's taxes")
    c.add_argument("--supplier-state", required=True, help="2-digit GST state code of the supplier")
    c.add_argument("--pos", required=True, help="2-digit place-of-supply code (96 = outside India)")
    c.add_argument("--item", action="append", default=[], help="'description,qty,unit_price,rate[,discount]'")
    c.add_argument("--items-json", help="JSON file: list of {description, qty, unit_price, rate, discount}")
    c.add_argument("--export-or-sez", action="store_true", help="Exports and SEZ supplies are inter-state")
    c.add_argument("--lut", action="store_true",
                   help="Zero-rated export/SEZ supply under a Letter of Undertaking: IGST 0")
    c.add_argument("--round-total", action="store_true", help="Round the total to the rupee, show round-off")
    n = sub.add_parser("invoice-no", help="Check an invoice number against Rule 46 and the e-invoice schema")
    n.add_argument("number")
    w = sub.add_parser("words", help="Amount in words, Indian system")
    w.add_argument("amount")
    f = sub.add_parser("format", help="Format with lakh/crore grouping")
    f.add_argument("amount")
    a = ap.parse_args(argv)
    if a.self_test:
        _self_test()
        return 0
    try:
        if a.cmd == "calc":
            items = [_parse_item(t) for t in a.item]
            if a.items_json:
                loaded = json.loads(Path(a.items_json).read_text(encoding="utf-8"))
                if not isinstance(loaded, list):
                    raise ValueError("--items-json must contain a JSON list of item objects")
                items += loaded
            if not items:
                ap.error("add at least one --item or --items-json")
            out = calc(items, a.supplier_state, a.pos, a.export_or_sez, a.round_total, a.lut)
        elif a.cmd == "invoice-no":
            out = check_invoice_no(a.number)
        elif a.cmd == "words":
            out = inr.amount_in_words(money(a.amount))
        elif a.cmd == "format":
            out = inr.format_inr(money(a.amount))
        else:
            ap.print_help()
            return 2
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError, InvalidOperation) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if a.json or a.cmd in ("invoice-no",):
        print(json.dumps(out, indent=2, default=_jsonable, ensure_ascii=False))
    elif a.cmd == "calc":
        print(f"Tax type: {out['tax_type']}  (supplier {a.supplier_state} -> place of supply {a.pos})")
        for ln in out["lines"]:
            taxes = "  ".join(f"{k} {inr.format_inr(ln[k])}" for k in ("CGST", "SGST", "UTGST", "IGST") if k in ln)
            print(f"  {ln['description'] or 'item':<20} taxable {inr.format_inr(ln['taxable_value']):>16}  @{ln['rate']}%  {taxes}")
        print(f"Taxable value  {inr.format_inr(out['taxable_value'])}")
        for k, v in out["taxes"].items():
            print(f"{k:<14} {inr.format_inr(v)}")
        if out["round_off"]:
            print(f"Round off      {out['round_off']}")
        print(f"Invoice total  {inr.format_inr(out['invoice_total'])}")
        print(out["amount_in_words"])
        if out["note"]:
            print(out["note"])
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
