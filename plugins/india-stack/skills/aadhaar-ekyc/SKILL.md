---
name: aadhaar-ekyc
description: Build identity verification in India safely - who may perform Aadhaar authentication and eKYC (Section 4(4) and the 2025 Good Governance amendment rules for private entities), offline verification with Secure QR and paperless offline e-KYC XML, the Aadhaar Data Vault with reference keys and HSM, masking to the last 4 digits, consent and notice under Section 8, the ban on storing biometrics, DigiLocker OAuth with PKCE, and RBI video KYC (V-CIP) and OTP e-KYC limits. Use when designing KYC onboarding, storing Aadhaar or identity documents, integrating DigiLocker or a KYC vendor, or reviewing identity code for India. Engineering guidance, not legal advice.
---

# Aadhaar, eKYC and DigiLocker

Aadhaar data carries criminal penalties when mishandled. Default to **not
storing the Aadhaar number at all**, and verify through a licensed provider or
an offline method. Facts checked against UIDAI, NeGD/API Setu and RBI sources
in **November 2026**; confirm with your compliance team and KYC provider.

## Who may authenticate

- Aadhaar authentication/eKYC is allowed only for entities permitted under the
  Aadhaar Act **s.4(4)**: by a law of Parliament, or for a purpose the Central
  Government prescribes. The **2025 Good Governance amendment rules** (31 January
  2025) let private entities apply, through the relevant ministry and UIDAI, for
  approved purposes.
- Approved entities operate as AUA/KUA or Sub-AUA/Sub-KUA, usually through a
  licensed provider. Do not call UIDAI APIs (or scrape Aadhaar portals) without that.
- Regulated entities (banks, NBFCs, payment companies) follow RBI's KYC
  Directions for which methods they may use.

## Consent and notice (s.8)

- Get consent before collecting identity information (from a parent or guardian
  for a child); use it only for authentication; tell the person what is shared,
  how it will be used and what alternatives exist; offer another way to identify
  them if authentication fails.
- Make Aadhaar optional where the law does not require it, and accept other
  officially valid documents.

## Storage rules

- **Biometrics:** never store or share core biometric information (s.29(1)).
- **Never publish or display** an Aadhaar number (s.29(4)); show it masked as
  `XXXX XXXX 1234` (last 4 digits only).
- **Aadhaar Data Vault** (UIDAI ADV FAQ, updated 3 November 2025): an entity that
  stores full Aadhaar numbers with connected data (eKYC XML, demographics, the
  Aadhaar PDF) must keep them in an encrypted vault backed by an **HSM (FIPS 140-2
  Level 3)**. Every other database stores a **reference key**, which must not be
  a hash of the Aadhaar number and must not allow recovering it. Access the vault
  only from internal systems.
- Aadhaar numbers typed in only to authenticate must not be stored in any form.
- Collected Aadhaar copies (for example in KYC uploads) should have the number
  redacted where authentication is not needed.

## Verification options

| Method | Notes |
|---|---|
| Licensed OTP / biometric eKYC (via a KUA) | Strongest for regulated onboarding; needs approval and a provider |
| **Secure QR code** (on Aadhaar letters, e-Aadhaar, mAadhaar) | UIDAI-signed; verify the signature offline |
| **Paperless offline e-KYC XML** | User downloads a signed, password-protected XML from UIDAI and shares it |
| Aadhaar app verifiable credentials | Selective disclosure (can share last 4 digits, demographics, photo) |
| **DigiLocker** | User consents to share UIDAI-issued e-Aadhaar or other issued documents |

Offline verification (s.8A) requires explicit consent, written disclosure of
each recipient and purpose, and end-to-end deletion if consent is revoked.

## DigiLocker integration

- Requester API (NeGD spec v1.12): OAuth 2.0 authorisation-code flow with
  **PKCE (S256 only)** at `https://api.digitallocker.gov.in/public/oauth2/1/authorize`
  and `/token`.
- **Issued documents** (pushed by government issuers, URI `IssuerId-DocType-DocId`)
  are deemed equivalent to originals under Rule 9A of the Digital Locker Rules;
  **uploaded documents** are user-supplied and not issuer-verified - treat them
  like any upload.
- Request only the scopes you need; store the document reference and
  verification result rather than copies where possible.

## RBI KYC (regulated entities)

From the RBI KYC Directions 2025 (28 November 2025):

- **Aadhaar OTP e-KYC (non-face-to-face):** specific consent; aggregate deposit
  balance up to ₹1 lakh; total credits up to ₹2 lakh per financial year; term
  loans only up to ₹60,000 a year; the account cannot run beyond one year without
  full CDD or V-CIP.
- **Video KYC (V-CIP):** liveness/spoof detection and face match, live GPS
  geotag with timestamp, block IPs outside India and spoofed IPs, end-to-end
  encryption, all data and recordings stored in India, concurrent audit before
  the account goes live.

## Review checklist

- [ ] Legal basis confirmed for any Aadhaar authentication; done through a licensed provider.
- [ ] Consent captured and logged with purpose; alternatives to Aadhaar offered.
- [ ] No biometrics stored; Aadhaar never logged or shown beyond the last 4 digits.
- [ ] Full Aadhaar numbers only in an HSM-backed vault; other systems use non-hash reference keys.
- [ ] Offline XML / Secure QR signatures verified against UIDAI's public key.
- [ ] DigiLocker: PKCE S256, minimal scopes, issued vs. uploaded treated differently.
- [ ] Regulated entities: OTP e-KYC limits enforced in the account system; V-CIP data kept in India.
