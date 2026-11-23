#!/usr/bin/env python3
"""Validate Indian identifiers: GSTIN (with check character), PAN, IFSC, Aadhaar
(Verhoeff), UPI VPA, PIN code and mobile numbers - and mask Aadhaar safely.

Part of claude-india-stack-skills by Viprasol Tech Private Limited.

Format checks catch typos; they do not prove an identifier exists or belongs to
someone. Verify against the issuing system (GST portal, NSDL/UTIITSL, bank,
UIDAI-licensed provider) when it matters. Standard library only.

  python india_validate.py gstin 27AAPFU0939F1ZV
  python india_validate.py pan ABCPE1234F
  python india_validate.py aadhaar 2345 6789 0124 --mask
  python india_validate.py auto 27AAPFU0939F1ZV HDFC0001234 ABCPE1234F
  python india_validate.py --self-test
"""

from __future__ import annotations

import argparse
import json
import re
import sys

ALNUM = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# GST state codes (IRP master list). 28 = pre-2014 Andhra Pradesh, still seen in
# older GSTINs; 97 = Other Territory; 99 = centre jurisdiction (label varies).
GST_STATE_CODES = {
    "01": "Jammu and Kashmir", "02": "Himachal Pradesh", "03": "Punjab", "04": "Chandigarh",
    "05": "Uttarakhand", "06": "Haryana", "07": "Delhi", "08": "Rajasthan", "09": "Uttar Pradesh",
    "10": "Bihar", "11": "Sikkim", "12": "Arunachal Pradesh", "13": "Nagaland", "14": "Manipur",
    "15": "Mizoram", "16": "Tripura", "17": "Meghalaya", "18": "Assam", "19": "West Bengal",
    "20": "Jharkhand", "21": "Odisha", "22": "Chhattisgarh", "23": "Madhya Pradesh", "24": "Gujarat",
    "25": "Daman and Diu", "26": "Dadra and Nagar Haveli and Daman and Diu", "27": "Maharashtra",
    "28": "Andhra Pradesh (old)", "29": "Karnataka", "30": "Goa", "31": "Lakshadweep", "32": "Kerala",
    "33": "Tamil Nadu", "34": "Puducherry", "35": "Andaman and Nicobar Islands", "36": "Telangana",
    "37": "Andhra Pradesh", "38": "Ladakh", "97": "Other Territory", "99": "Centre Jurisdiction",
}

PAN_ENTITY = {
    "P": "individual", "C": "company", "H": "Hindu undivided family", "F": "firm / LLP",
    "A": "association of persons", "T": "trust", "B": "body of individuals",
    "L": "local authority", "J": "artificial juridical person", "G": "government",
}

PAN_RE = re.compile(r"^[A-Z]{3}[ABCFGHJLPT][A-Z][0-9]{4}[A-Z]$")
IFSC_RE = re.compile(r"^[A-Z]{4}0[A-Z0-9]{6}$")
PIN_RE = re.compile(r"^[1-9][0-9]{5}$")
MOBILE_RE = re.compile(r"^[6-9][0-9]{9}$")
VPA_RE = re.compile(r"^[A-Za-z0-9._-]{2,256}@[A-Za-z]{2,64}$")  # permissive; no public NPCI spec

# Verhoeff tables
_D = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 2, 3, 4, 0, 6, 7, 8, 9, 5], [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
      [3, 4, 0, 1, 2, 8, 9, 5, 6, 7], [4, 0, 1, 2, 3, 9, 5, 6, 7, 8], [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
      [6, 5, 9, 8, 7, 1, 0, 4, 3, 2], [7, 6, 5, 9, 8, 2, 1, 0, 4, 3], [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
      [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]]
_P = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 5, 7, 6, 2, 8, 3, 0, 9, 4], [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
      [8, 9, 1, 6, 0, 4, 3, 5, 2, 7], [9, 4, 5, 3, 1, 2, 6, 8, 7, 0], [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
      [2, 7, 9, 3, 8, 0, 6, 4, 1, 5], [7, 0, 4, 6, 9, 1, 3, 2, 5, 8]]


def verhoeff_ok(digits: str) -> bool:
    c = 0
    for i, ch in enumerate(reversed(digits)):
        c = _D[c][_P[i % 8][int(ch)]]
    return c == 0


def gstin_check_char(first14: str) -> str:
    """Luhn mod 36 over the first 14 characters (weights 1, 2, 1, 2, ...)."""
    total = 0
    for i, ch in enumerate(first14):
        p = ALNUM.index(ch) * (2 if i % 2 else 1)
        total += p // 36 + p % 36
    return ALNUM[(36 - total % 36) % 36]


def _clean(value: str) -> str:
    return re.sub(r"[\s-]", "", value).upper()


def check_gstin(value: str) -> dict:
    v = _clean(value)
    res = {"type": "gstin", "value": v, "valid": False, "errors": [], "info": {}}
    if len(v) != 15 or any(ch not in ALNUM for ch in v):
        res["errors"].append("must be 15 letters/digits")
        return res
    if v[:2] not in GST_STATE_CODES:
        res["errors"].append(f"unknown state code {v[:2]}")
    else:
        res["info"]["state"] = GST_STATE_CODES[v[:2]]
    expected = gstin_check_char(v[:14])
    if v[14] != expected:
        res["errors"].append(f"check character is {v[14]}, expected {expected} (typo?)")
    if PAN_RE.match(v[2:12]):
        res["info"]["pan"] = v[2:12]
        res["info"]["entity"] = PAN_ENTITY[v[5]]
    else:
        # Non-resident, TDS/TCS, UN-body and OIDAR registrations use other middle formats.
        res["info"]["note"] = "characters 3-12 are not a PAN: special registration type, or a typo"
    res["valid"] = not res["errors"]
    return res


def check_pan(value: str) -> dict:
    v = _clean(value)
    ok = bool(PAN_RE.match(v))
    res = {"type": "pan", "value": v, "valid": ok, "errors": [] if ok else ["expected AAAAA9999A with a valid 4th-character entity code"], "info": {}}
    if ok:
        res["info"]["entity"] = PAN_ENTITY[v[3]]
        res["info"]["note"] = "the final letter is a check character whose algorithm is not public"
    return res


def check_ifsc(value: str) -> dict:
    v = _clean(value)
    ok = bool(IFSC_RE.match(v))
    return {"type": "ifsc", "value": v, "valid": ok,
            "errors": [] if ok else ["expected 4 letters (bank) + '0' + 6 letters/digits (branch)"],
            "info": {"bank_code": v[:4]} if ok else {}}


def mask_aadhaar(value: str) -> str:
    v = re.sub(r"\D", "", value)
    return "XXXX XXXX " + v[-4:] if len(v) == 12 else "XXXX XXXX XXXX"


def check_aadhaar(value: str) -> dict:
    v = re.sub(r"[\s-]", "", value)
    errors = []
    if not re.fullmatch(r"[2-9][0-9]{11}", v):
        errors.append("must be 12 digits and not start with 0 or 1")
    elif not verhoeff_ok(v):
        errors.append("Verhoeff check digit does not match (typo?)")
    # Never echo the full number back: return only the masked form.
    return {"type": "aadhaar", "value": mask_aadhaar(v), "valid": not errors, "errors": errors,
            "info": {"note": "store only in an encrypted Aadhaar Data Vault; display only the last 4 digits"}}


def check_vpa(value: str) -> dict:
    v = value.strip()
    ok = bool(VPA_RE.match(v))
    return {"type": "vpa", "value": v, "valid": ok,
            "errors": [] if ok else ["expected name@handle"],
            "info": {"note": "format only; confirm with a VPA verification/name-lookup call before paying"}}


def check_pin(value: str) -> dict:
    v = _clean(value)
    ok = bool(PIN_RE.match(v))
    return {"type": "pin", "value": v, "valid": ok, "errors": [] if ok else ["expected 6 digits, first digit 1-9"], "info": {}}


def _tail(value: str) -> str:
    """Show only the last 4 characters of a value that failed validation."""
    v = re.sub(r"\s", "", value)
    return ("*" * max(0, len(v) - 4)) + v[-4:]


def check_mobile(value: str) -> dict:
    v = re.sub(r"[\s-]", "", value)
    v = re.sub(r"^(\+91|0091|91(?=\d{10}$)|0(?=\d{10}$))", "", v)
    ok = bool(MOBILE_RE.match(v))
    return {"type": "mobile", "value": v if ok else _tail(v), "valid": ok,
            "errors": [] if ok else ["expected a 10-digit Indian mobile starting 6-9 (optional +91)"], "info": {}}


CHECKS = {"gstin": check_gstin, "pan": check_pan, "ifsc": check_ifsc, "aadhaar": check_aadhaar,
          "vpa": check_vpa, "pin": check_pin, "mobile": check_mobile}


def detect(value: str) -> str | None:
    v = _clean(value)
    if "@" in value:
        return "vpa"
    if len(v) == 15:
        return "gstin"
    if len(v) == 11 and IFSC_RE.match(v):
        return "ifsc"
    if len(v) == 10 and v[:5].isalpha():
        return "pan"
    digits = re.sub(r"\D", "", value)
    if len(digits) == 12 and digits.startswith("91") and MOBILE_RE.match(digits[2:]):
        return None  # could be 91 + mobile or an Aadhaar number: ask for the type
    if len(digits) == 12 and digits[0] in "23456789" and not value.strip().startswith("+"):
        return "aadhaar"
    if len(v) == 6 and v.isdigit():
        return "pin"
    if len(digits) in (10, 12, 13):
        return "mobile"
    return None


def _self_test() -> None:
    assert gstin_check_char("27AAPFU0939F1Z") == "V"
    assert gstin_check_char("27AACCM9910C1Z") == "N"
    g = check_gstin("27aapfu0939f1zv")
    assert g["valid"] and g["info"]["state"] == "Maharashtra" and g["info"]["entity"] == "firm / LLP", g
    bad = check_gstin("27AAPFU0939F1ZX")
    assert not bad["valid"] and "expected V" in bad["errors"][0]
    assert not check_gstin("00AAPFU0939F1ZV")["valid"]
    assert check_pan("ABCPE1234F")["valid"] and check_pan("abcpe1234f")["info"]["entity"] == "individual"
    assert not check_pan("ABCXE1234F")["valid"] and not check_pan("ABCP1234F")["valid"]
    assert check_ifsc("HDFC0001234")["valid"] and not check_ifsc("HDFC1001234")["valid"]
    # Verhoeff: 23456789012 + computed check digit
    base = "23456789012"
    good = next(base + str(d) for d in range(10) if verhoeff_ok(base + str(d)))
    a = check_aadhaar(good)
    assert a["valid"] and a["value"] == "XXXX XXXX " + good[-4:] and good not in json.dumps(a)
    wrong = base + str((int(good[-1]) + 1) % 10)
    assert not check_aadhaar(wrong)["valid"] and not check_aadhaar("123456789012")["valid"]
    assert check_vpa("asha.k@okhdfcbank")["valid"] and not check_vpa("asha.k")["valid"]
    assert check_pin("560001")["valid"] and not check_pin("060001")["valid"]
    for m in ["9876543210", "+91 98765 43210", "09876543210", "919876543210"]:
        assert check_mobile(m)["valid"], m
    assert not check_mobile("5876543210")["valid"]
    assert detect("27AAPFU0939F1ZV") == "gstin" and detect("HDFC0001234") == "ifsc"
    assert detect("919876543210") is None  # 91 + mobile: ambiguous with Aadhaar
    m = check_mobile("234567890124")
    assert not m["valid"] and m["value"] == "********0124", m
    assert detect("ABCPE1234F") == "pan" and detect("a@okaxis") == "vpa" and detect("560001") == "pin"
    print("india_validate self-test passed")


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Validate Indian identifiers")
    ap.add_argument("kind", nargs="?", choices=[*CHECKS, "auto"])
    ap.add_argument("values", nargs="*")
    ap.add_argument("--mask", action="store_true", help="Print a masked Aadhaar (last 4 only)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        _self_test()
        return 0
    if not a.kind or not a.values:
        ap.error("kind and at least one value are required (or use --self-test)")
    if a.kind == "aadhaar" and a.mask:
        print(mask_aadhaar(" ".join(a.values)))
        return 0
    values = [" ".join(a.values)] if a.kind in ("aadhaar", "mobile") else a.values
    results = []
    for v in values:
        kind = detect(v) if a.kind == "auto" else a.kind
        results.append(CHECKS[kind](v) if kind else {"type": "unknown", "value": _tail(v), "valid": False,
                                                      "errors": ["ambiguous or unknown type: name it explicitly (e.g. aadhaar, mobile)"],
                                                      "info": {}})
    if a.json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            status = "VALID" if r["valid"] else "INVALID"
            extra = "; ".join(f"{k}: {v}" for k, v in r["info"].items())
            print(f"{r['type']:<8}{r['value']:<20}{status}" + (f"  ({extra})" if extra else ""))
            for e in r["errors"]:
                print(f"        - {e}")
    return 0 if all(r["valid"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
