<div align="center">

<img src=".github/social-preview.png" alt="Claude India Stack Skills: Claude Code skills for building in India - UPI, GST, Aadhaar, Account Aggregator, DPDP." width="100%">

### Claude Code skills for building products in India

**UPI · GST & e-invoicing · PAN / GSTIN / IFSC / Aadhaar · eKYC & DigiLocker · Account Aggregator · RBI rules · DPDP Act**<br>
Generic AI coding tools don't know NPCI circulars, Rule 46 or the Aadhaar Data Vault. These skills do.

[![Stars](https://img.shields.io/github/stars/Viprasol-Tech/claude-india-stack-skills?style=for-the-badge&logo=github&color=d9ae58)](https://github.com/Viprasol-Tech/claude-india-stack-skills/stargazers)
[![License: MIT](https://img.shields.io/badge/license-MIT-25342f?style=for-the-badge)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude_Code-skills_%2B_plugin-d97757?style=for-the-badge)](https://code.claude.com/docs/en/skills)
[![Skills](https://img.shields.io/badge/skills-7-765820?style=for-the-badge)](#-whats-inside)
[![CI](https://img.shields.io/github/actions/workflow/status/Viprasol-Tech/claude-india-stack-skills/ci.yml?branch=main&style=for-the-badge&label=tests)](https://github.com/Viprasol-Tech/claude-india-stack-skills/actions/workflows/ci.yml)

[Quick start](#-quick-start) · [What's inside](#-whats-inside) · [Examples](#-just-ask) · [Scripts](#-bundled-scripts) · [Changelog](CHANGELOG.md)

</div>

---

## 💬 Just ask

Install once, then talk to Claude Code normally. The right skill loads by itself.

```text
> Add UPI checkout to our Next.js store: intent on mobile, QR on desktop, no double fulfilment.
> Our UPI orders get stuck in "pending". How often may we call check-status?
> Build GST invoices: we're in Maharashtra, the buyer is in Karnataka. Which tax applies?
> Validate GSTIN, PAN and IFSC on our vendor onboarding form.
> We need e-invoicing - our turnover just crossed 5 crore. What changes?
> Design KYC with DigiLocker and Aadhaar offline XML. What may we store?
> Pull 6 months of bank statements through an Account Aggregator for loan underwriting.
> Are we ready for the DPDP Rules? Review our signup, consent and deletion flows.
```

## 📦 What's inside

| Skill | What it does |
| --- | --- |
| 📲 **`upi-payments`** | `upi://pay` links and QR, intent vs. QR vs. collect, NPCI's 2026 status-check rules (first check after 60 s, max 3), 15-second timeouts, peak-hour limits, UPI Lite, AutoPay mandates, refunds and RBI reversal timelines. |
| 🧾 **`gst-invoicing`** | CGST+SGST vs. IGST vs. UTGST from place of supply, GST 2.0 slabs (from 22 Sep 2025), Rule 46 fields and 16-character numbering, HSN digits, e-invoicing with IRN/QR, the 30-day IRP limit, e-way bills and rounding. |
| ✅ **`india-data-validation`** | GSTIN with its mod-36 check character, PAN entity codes, IFSC, Aadhaar Verhoeff check and masking, UPI VPA, PIN, +91 mobile, lakh/crore formatting and IST. |
| 🪪 **`aadhaar-ekyc`** | Who may authenticate (s.4(4) and the 2025 rules), offline XML and Secure QR, the HSM-backed Aadhaar Data Vault with reference keys, masking, DigiLocker OAuth with PKCE, RBI OTP e-KYC limits and video KYC. |
| 🔗 **`account-aggregator`** | FIU/FIP/AA roles, RBI's NBFC-AA Directions 2025, consent artefacts, revocation, ReBIT v2 flows, Sahamati certification and available FI types. |
| 🏦 **`rbi-payment-rules`** | No card storage and tokenisation, payment data localisation, the 2025 Payment Aggregator Directions, 2026 e-mandate and authentication rules, failed-transaction compensation. |
| 🔒 **`dpdp-privacy`** | DPDP Act 2023 + Rules 2025: commencement dates, notice and consent, security and log retention, 72-hour breach reports, 3-year erasure, children's data, SDF duties and penalties. |

Every regulatory fact links to its official source (NPCI, RBI, CBIC/GSTN, NIC
IRP, UIDAI, NeGD/API Setu, ReBIT, Sahamati, MeitY) and was **checked in
November 2026**.

## ⚡ Quick start

**Option A: Claude Code plugin (recommended)**

```bash
claude plugin marketplace add Viprasol-Tech/claude-india-stack-skills
claude plugin install india-stack@claude-india-stack-skills
```

Skills are then available as `/india-stack:<skill>` and load automatically when
your request matches.

**Option B: installer** (copies the skills to `~/.claude/skills`)

```bash
git clone https://github.com/Viprasol-Tech/claude-india-stack-skills
cd claude-india-stack-skills
bash install.sh                                        # macOS / Linux
powershell -ExecutionPolicy Bypass -File install.ps1   # Windows
```

No API keys, no accounts, no network calls. The scripts need only Python 3.10+.

## 🧰 Bundled scripts

**`gst.py`** - invoice maths with the right tax type:

```text
$ python gst.py calc --supplier-state 27 --pos 29 --item "Consulting,1,100000.40,18" --round-total
Tax type: IGST  (supplier 27 -> place of supply 29)
Taxable value  ₹1,00,000.40
IGST           ₹18,000.07
Round off      -0.47
Invoice total  ₹1,18,000.00
Rupees One Lakh Eighteen Thousand Only
```

**`india_validate.py`** - catch typos before they reach the GST portal or a payout:

```text
$ python india_validate.py auto 27AAPFU0939F1ZX HDFC0001234 ABCPE1234F
gstin   27AAPFU0939F1ZX     INVALID  (state: Maharashtra; ...)
        - check character is X, expected V (typo?)
ifsc    HDFC0001234         VALID  (bank_code: HDFC)
pan     ABCPE1234F          VALID  (entity: individual; ...)
```

Aadhaar is only ever printed masked (`XXXX XXXX 1234`).

**`upi_link.py`** - build and inspect UPI links and QR payloads:

```text
$ python upi_link.py build --pa shop@okaxis --pn "Asha Stores" --am 499 --tr ORD-1001 --mode 01
upi://pay?pa=shop@okaxis&pn=Asha%20Stores&tr=ORD-1001&am=499.00&cu=INR&mode=01
```

## 🗂️ Repository layout

```text
.claude-plugin/marketplace.json          marketplace manifest
plugins/india-stack/
  .claude-plugin/plugin.json             plugin manifest
  skills/<skill>/SKILL.md                one folder per skill
  skills/gst-invoicing/scripts/          gst.py, inr.py
  skills/india-data-validation/scripts/  india_validate.py
  skills/upi-payments/scripts/           upi_link.py
tests/validate_repo.py                   CI: manifests, frontmatter, links, scripts
```

## ⚠️ Disclaimer

These skills are **engineering guidance**, not legal, tax or compliance advice.
NPCI, RBI, GST, UIDAI and data-protection rules change frequently; confirm the
current circular, notification or rule before relying on a limit, rate or
deadline, and consult a qualified professional. Format checks do not prove an
identifier is genuine. Never paste real Aadhaar, PAN, bank or card details into
a chat. Viprasol Tech is not affiliated with NPCI, RBI, GSTN, UIDAI, NeGD,
Sahamati, MeitY, Anthropic or any payment provider mentioned here.

## 🤝 Contributing

Corrections with a link to the official circular or notification are the most
valuable contribution. See [CONTRIBUTING.md](CONTRIBUTING.md) and run
`python tests/validate_repo.py` before opening a PR. More free Claude Code packs
from Viprasol:
[claude-crypto-bot-skills](https://github.com/Viprasol-Tech/claude-crypto-bot-skills) ·
[claude-voice-agent-skills](https://github.com/Viprasol-Tech/claude-voice-agent-skills) ·
[claude-fintech-skills](https://github.com/Viprasol-Tech/claude-fintech-skills) ·
[claude-trading-skills](https://github.com/Viprasol-Tech/claude-trading-skills) ·
[claude-video-editing-skills](https://github.com/Viprasol-Tech/claude-video-editing-skills).

## 📬 Contact — Viprasol Tech Private Limited

Building a UPI, lending, wealth or GST product for India? We design and build
fintech platforms end to end.

- 🌐 Website: [viprasol.com](https://viprasol.com)
- ✉️ Email: [support@viprasol.com](mailto:support@viprasol.com)
- 💬 Telegram: [t.me/viprasol_help](https://t.me/viprasol_help) · 📱 WhatsApp: +91 96336 52112
- 🐙 GitHub: [@Viprasol-Tech](https://github.com/Viprasol-Tech) · 💼 [LinkedIn](https://www.linkedin.com/in/viprasol/) · 𝕏 [@viprasol](https://twitter.com/viprasol)

## License

[MIT](LICENSE) © 2026 Viprasol Tech Private Limited
