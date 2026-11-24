---
name: india-data-validation
description: Validate and handle Indian identifiers and formats correctly - GSTIN with its mod-36 check character and state code, PAN structure and entity type, IFSC, Aadhaar with Verhoeff check digit and mandatory masking, UPI VPA, PIN codes, +91 mobile numbers, lakh/crore number formatting, INR paise and IST. Includes a tested validator that never echoes a full Aadhaar number. Use when building signup, KYC, invoicing, payout or address forms for India, writing validation regexes, or reviewing code that stores Indian identifiers.
allowed-tools: Bash(python ${CLAUDE_SKILL_DIR}/scripts/india_validate.py *)
---

# Indian data validation

Format checks stop typos early; they do **not** prove an identifier exists or
belongs to the user. For that, verify with the issuing system (GST portal,
PAN verification providers, penny-drop for bank accounts, UIDAI-licensed eKYC).
Validate structure in the UI and API, verify ownership in the backend.

## Identifier rules

| Identifier | Rule | Notes |
|---|---|---|
| **GSTIN** | 15 chars: 2-digit state code + 10-char PAN + entity number + `Z` (usually) + check character | Check character = Luhn mod 36 over the first 14 characters (0-9, A-Z; weights 1,2,1,2...). `27AAPFU0939F1ZV` is valid. Some registrations (non-resident, TDS/TCS, UN bodies, OIDAR) do not embed a PAN: reject on checksum and state code, not on the middle format. |
| **PAN** | `[A-Z]{3}[ABCFGHJLPT][A-Z][0-9]{4}[A-Z]` | 4th character = holder type: P individual, C company, H HUF, F firm/LLP, A AOP, T trust, B BOI, L local authority, J artificial juridical person, G government. The last letter is a check character with no published algorithm. |
| **IFSC** | `^[A-Z]{4}0[A-Z0-9]{6}$` | Bank code + reserved `0` + branch code. Look up the branch from RBI's IFSC list or a maintained dataset. |
| **Aadhaar** | 12 digits, first digit 2-9, last digit a **Verhoeff** check digit | Display only the last 4 (`XXXX XXXX 1234`); store only in an Aadhaar Data Vault (see `aadhaar-ekyc`). |
| **UPI VPA** | `name@handle` | No public NPCI character spec; validate permissively and confirm with a VPA lookup before paying. |
| **PIN code** | `^[1-9][0-9]{5}$` | First digit is the postal zone (9 = Army Postal Service). |
| **Mobile** | `^[6-9][0-9]{9}$` after stripping `+91`, `0091`, `91` or a leading `0` | Store in E.164 (`+919876543210`). |

GST state codes follow the IRP master list: 01 Jammu and Kashmir ... 37 Andhra
Pradesh, 38 Ladakh, 97 Other Territory, 99 Centre Jurisdiction, 96 for supplies
outside India; 28 appears in older (pre-2014 Andhra Pradesh) GSTINs.

## Validator

```bash
python ${CLAUDE_SKILL_DIR}/scripts/india_validate.py gstin 27AAPFU0939F1ZV
python ${CLAUDE_SKILL_DIR}/scripts/india_validate.py pan ABCPE1234F
python ${CLAUDE_SKILL_DIR}/scripts/india_validate.py ifsc HDFC0001234
python ${CLAUDE_SKILL_DIR}/scripts/india_validate.py aadhaar 2345 6789 0124          # prints only the masked number
python ${CLAUDE_SKILL_DIR}/scripts/india_validate.py aadhaar 234567890124 --mask     # XXXX XXXX 0124
python ${CLAUDE_SKILL_DIR}/scripts/india_validate.py mobile "+91 98765 43210"
python ${CLAUDE_SKILL_DIR}/scripts/india_validate.py auto 27AAPFU0939F1ZV HDFC0001234 ABCPE1234F asha@okicici
python ${CLAUDE_SKILL_DIR}/scripts/india_validate.py --json gstin 27AAPFU0939F1ZV
```

Exit code is 0 only if every value is valid, so it works in scripts and CI.

## Formats

- **Numbers:** Indian grouping is `12,34,56,789.00` (last three digits, then
  pairs). Use `Intl.NumberFormat('en-IN', {style: 'currency', currency: 'INR'})`,
  Babel/ICU `en_IN`, or the `gst-invoicing` skill's formatter. Words use lakh
  (1,00,000) and crore (1,00,00,000).
- **Money:** ₹1 = 100 paise; store integer paise or Decimal (see
  `claude-fintech-skills` money-math if installed).
- **Time:** India Standard Time is UTC+05:30 with no daylight saving. Store UTC,
  display IST; financial year runs 1 April - 31 March (matters for GST invoice
  numbering and reports).
- **Names and addresses:** do not force first/last name splits; many people use
  a single name. Keep state as a code from a fixed list.

## Review checklist

- [ ] Regexes match the table above (common bug: PAN without the 4th-character set,
      IFSC without the `0`, mobile starting with any digit).
- [ ] GSTIN check character verified, and the state code matches the address state.
- [ ] Inputs normalised (trim, uppercase, remove spaces/dashes) before validation and storage.
- [ ] Aadhaar never logged, never shown in full, never stored outside a vault.
- [ ] Ownership verified with the issuer where it matters (payouts, KYC, invoicing).
- [ ] Amounts formatted with en-IN grouping; IST used for display, UTC for storage.
