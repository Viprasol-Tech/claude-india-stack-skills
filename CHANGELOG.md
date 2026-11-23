# Changelog

All notable changes are listed here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [1.0.0] - 2026-11-23

### Added
- `india-stack` Claude Code plugin with 7 skills: `upi-payments`,
  `gst-invoicing`, `india-data-validation`, `aadhaar-ekyc`,
  `account-aggregator`, `rbi-payment-rules`, `dpdp-privacy`.
- `gst.py` + `inr.py`: CGST/SGST/UTGST/IGST split, paise rounding with
  round-off, Rule 46 and e-invoice number checks, lakh/crore formatting and
  amount in words.
- `india_validate.py`: GSTIN (mod-36 check character and state code), PAN,
  IFSC, Aadhaar (Verhoeff, masked output only), UPI VPA, PIN code and mobile.
- `upi_link.py`: build and inspect `upi://pay` links and QR payloads.
- Facts checked against NPCI, RBI, CBIC/GSTN, UIDAI, NeGD, ReBIT/Sahamati and
  MeitY sources in November 2026.
