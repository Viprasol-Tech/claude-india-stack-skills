#!/usr/bin/env python3
"""Build and inspect UPI payment links (upi://pay?...), the same string a UPI QR encodes.

Part of claude-india-stack-skills by Viprasol Tech Private Limited.

Parameters follow NPCI's UPI Linking Specification (pa, pn, am, cu, tr, tn, mc,
mode, url...). This tool builds unsigned links for testing and for flows where
your PSP or payment aggregator signs or generates the final intent/QR. Never
treat a payment as successful because the app returned to you: confirm the
status with your PSP or bank server. Standard library only.

  python upi_link.py build --pa shop@okaxis --pn "Asha Stores" --am 499 --tr ORD-1001 --tn "Order 1001"
  python upi_link.py parse "upi://pay?pa=shop@okaxis&pn=Asha%20Stores&am=499.00&cu=INR&tr=ORD-1001"
  python upi_link.py --self-test
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from decimal import Decimal, InvalidOperation
from urllib.parse import parse_qsl, quote, urlsplit

VPA_RE = re.compile(r"^[A-Za-z0-9._-]{2,256}@[A-Za-z]{2,64}$")
AMOUNT_RE = re.compile(r"^\d+(\.\d{1,2})?$")
KNOWN = ["pa", "pn", "mc", "tid", "tr", "tn", "am", "mam", "cu", "url", "mode", "orgid",
         "mid", "msid", "mtid", "purpose", "sign"]
MODES = {"00": "default", "01": "QR", "02": "secure QR", "04": "intent", "05": "secure intent",
         "06": "NFC", "07": "BLE", "08": "UHF", "15": "SEBI"}


def _amount(value: str) -> str:
    if not AMOUNT_RE.match(str(value)):
        raise ValueError(f"amount must be plain rupees with up to 2 decimals, got {value!r}")
    try:
        d = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"amount must be a number, got {value!r}") from exc
    if not d.is_finite() or d <= 0 or d >= Decimal("1e12"):
        raise ValueError("amount must be positive and realistic")
    if d != d.quantize(Decimal("0.01")):
        raise ValueError("amount has more than 2 decimal places (paise)")
    return f"{d:.2f}"


def build(pa: str, pn: str, am: str | None = None, tr: str | None = None, tn: str | None = None,
          mc: str | None = None, mode: str | None = None, url: str | None = None) -> str:
    if not VPA_RE.match(pa):
        raise ValueError(f"payee VPA looks invalid: {pa!r}")
    if not pn.strip():
        raise ValueError("payee name (pn) is required")
    params: list[tuple[str, str]] = [("pa", pa), ("pn", pn.strip())]
    if mc:
        if not re.fullmatch(r"\d{4}", mc):
            raise ValueError("mc (merchant category code) must be 4 digits")
        params.append(("mc", mc))
    if tr:
        params.append(("tr", tr))
    if tn:
        params.append(("tn", tn))
    if am is not None:
        params.append(("am", _amount(am)))
    params.append(("cu", "INR"))
    if mode:
        if mode not in MODES:
            raise ValueError(f"mode must be one of {', '.join(MODES)}")
        params.append(("mode", mode))
    if url:
        if not url.startswith(("https://", "http://")):
            raise ValueError("url must be http(s) and about this transaction only")
        params.append(("url", url))
    # Percent-encode values (spaces become %20, never '+').
    return "upi://pay?" + "&".join(f"{k}={quote(v, safe='@.-_')}" for k, v in params)


def parse(link: str) -> dict:
    parts = urlsplit(link)
    if parts.scheme.lower() != "upi" or parts.netloc.lower() != "pay":
        raise ValueError("not a upi://pay link")
    pairs = parse_qsl(parts.query, keep_blank_values=True)
    fragment_lost = bool(parts.fragment)
    keys = [k for k, _ in pairs]
    fields = dict(pairs)
    issues, warnings = [], []
    if fragment_lost:
        issues.append("unencoded '#': everything after it was dropped; encode it as %23")
    if len(set(keys)) != len(keys):
        issues.append("duplicate parameters")
    for req in ("pa", "pn"):
        if not fields.get(req):
            issues.append(f"missing {req}")
    if fields.get("pa") and not VPA_RE.match(fields["pa"]):
        issues.append("pa is not a valid-looking VPA")
    if "cu" in fields and fields["cu"] != "INR":
        issues.append("cu must be INR")
    if "am" in fields:
        try:
            _amount(fields["am"])
        except ValueError as exc:
            issues.append(f"am: {exc}")
    else:
        warnings.append("no am: the payer can edit the amount (static QR behaviour)")
    if "tr" not in fields:
        warnings.append("no tr: merchant and dynamic links need a transaction reference")
    if "sign" in fields and keys[-1] != "sign":
        issues.append("sign must be the last parameter")
    if "sign" not in fields:
        warnings.append("unsigned: payer apps may warn that the source could not be verified")
    unknown = [k for k in keys if k not in KNOWN]
    if unknown:
        warnings.append(f"unknown parameters: {', '.join(unknown)}")
    if "mode" in fields:
        fields["mode_name"] = MODES.get(fields["mode"], "unknown")
    return {"fields": fields, "valid": not issues, "issues": issues, "warnings": warnings}


def _self_test() -> None:
    link = build("shop@okaxis", "Asha Stores", "499", "ORD-1001", "Order 1001")
    assert link == "upi://pay?pa=shop@okaxis&pn=Asha%20Stores&tr=ORD-1001&tn=Order%201001&am=499.00&cu=INR", link
    p = parse(link)
    assert p["valid"] and p["fields"]["pn"] == "Asha Stores" and p["fields"]["am"] == "499.00"
    assert any("unsigned" in w for w in p["warnings"])
    for bad in [lambda: build("shop", "X"), lambda: build("shop@okaxis", "X", "0"),
                lambda: build("shop@okaxis", "X", "1.005"), lambda: build("shop@okaxis", "X", mode="03"),
                lambda: build("shop@okaxis", "X", "1e2"), lambda: build("shop@okaxis", "X", "1e30")]:
        try:
            bad()
        except ValueError:
            pass
        else:
            raise AssertionError("must reject")
    q = parse("upi://pay?pa=a@okaxis&pn=A&am=10&cu=USD&sign=abc&tr=1")
    assert not q["valid"] and "cu must be INR" in q["issues"] and "sign must be the last parameter" in q["issues"]
    assert not parse("upi://pay?pn=A")["valid"]
    assert not parse("upi://pay?pa=shop@okaxis&pn=A&tn=a#b&am=5")["valid"]
    assert not parse("upi://pay?pa=shop@okaxis&pn=A&am=1e2&tr=1")["valid"]
    rt = parse(build("shop@okaxis", "A & B #1 50%+", "10", "T-1", "नमस्ते"))
    assert rt["valid"] and rt["fields"]["pn"] == "A & B #1 50%+" and rt["fields"]["tn"] == "नमस्ते"
    try:
        parse("https://example.com/pay?pa=a@b")
    except ValueError:
        pass
    else:
        raise AssertionError("non-upi link accepted")
    print("upi_link self-test passed")


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Build and inspect UPI payment links")
    ap.add_argument("--self-test", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    b = sub.add_parser("build", help="Build an unsigned upi://pay link")
    b.add_argument("--pa", required=True, help="Payee VPA")
    b.add_argument("--pn", required=True, help="Payee name")
    b.add_argument("--am", help="Amount in rupees (omit for payer-entered amount)")
    b.add_argument("--tr", help="Your order / transaction reference")
    b.add_argument("--tn", help="Note shown to the payer")
    b.add_argument("--mc", help="4-digit merchant category code")
    b.add_argument("--mode", help="Initiation mode, e.g. 01 QR, 04 intent")
    b.add_argument("--url", help="https link to the invoice for this transaction")
    p = sub.add_parser("parse", help="Inspect a upi://pay link or QR payload")
    p.add_argument("link")
    a = ap.parse_args(argv)
    if a.self_test:
        _self_test()
        return 0
    try:
        if a.cmd == "build":
            print(build(a.pa, a.pn, a.am, a.tr, a.tn, a.mc, a.mode, a.url))
            return 0
        if a.cmd == "parse":
            res = parse(a.link)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return 0 if res["valid"] else 1
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
