---
name: account-aggregator
description: Integrate India's Account Aggregator (AA) framework for consent-based financial data sharing - roles (FIU, FIP, AA), RBI's NBFC-AA Directions 2025, consent artefacts (purpose, FI types, date range, frequency, data life, expiry), revocation, data-blind and encrypted flows, ReBIT API specifications (v2.x), Sahamati certification, and available FI types such as deposits, mutual funds, equities, insurance, NPS and GST returns. Use when building lending, wealth, personal finance or underwriting features that pull bank statements or portfolio data in India, or reviewing AA integration code. Engineering guidance, not legal advice.
---

# Account Aggregator integration

Account Aggregators let a customer share financial data from one regulated
entity to another with explicit, revocable consent - replacing PDF bank
statements and credential scraping. Checked against RBI, ReBIT and Sahamati
sources in **November 2026**.

## Roles

| Role | Who | In your build |
|---|---|---|
| **FIP** (Financial Information Provider) | bank, AMC/RTA, depository, insurer, NPS, GSTN | holds the data |
| **FIU** (Financial Information User) | lender, wealth app, insurer... | requests the data - **must be regulated** by RBI, SEBI, IRDAI, PFRDA or the Department of Revenue |
| **AA** (Account Aggregator) | RBI-licensed NBFC-AA | carries consent and encrypted data; cannot read it |

Unregulated apps cannot be FIUs; they partner with a regulated FIU or use the
FIU's technology service provider.

## Rules that shape the design (NBFC-AA Directions 2025)

RBI's **NBFC - Account Aggregator Directions, 2025** (28 November 2025) replace
the 2016 master direction:

- Data flows **only on the customer's explicit consent** through a consent
  artefact (para 17) recording identity, the nature of information, purpose,
  recipients, a notification URL, and creation and expiry dates.
- Customers can **revoke** consent at any time (para 20) - stop fetching and
  honour the data-life limits.
- AAs hold no customer financial information (data-blind, para 14(7)) and never
  see customer credentials. FIPs digitally sign and securely transmit data.
- Entities adopt the **ReBIT** technical specifications as updated (para 33).

## Consent artefact (ReBIT schema)

Design your consent request around the fields the ReBIT specs define (confirm
names against the current spec, v2.x at <https://api.rebit.org.in>):

- **Purpose** (code and text) - be specific; customers see it.
- **FI types** - only those you need (for example `DEPOSIT`, `MUTUAL_FUNDS`,
  `EQUITIES`, `INSURANCE_POLICIES`, `NPS`, `GSTR1_3B`).
- **FI data range** - from/to dates of history requested.
- **Consent mode / fetch type** - one-time vs. periodic, with a **frequency**.
- **Data life** - how long you may keep fetched data; delete it after.
- **Consent start and expiry.**

Ask for the minimum: a lender needing 6 months of statements should not request
5 years of periodic access.

## Integration flow

```text
FIU backend -> AA: create consent request (purpose, FI types, range, frequency, data life)
customer    -> AA app/web: approves (selects accounts at FIPs)
AA          -> FIU: consent approved notification (consent handle -> consent id)
FIU         -> AA: FI request with ephemeral public key (key exchange per ReBIT spec)
FIP         -> (via AA, encrypted) -> FIU: signed financial data
FIU         : decrypt, verify FIP signature, parse to the FI schema, store per data life
```

- Handle every state: pending, rejected, paused, revoked, expired.
- Verify signatures on notifications and data; never log decrypted statements.
- Use Sahamati-certified AA and FIP integrations; Sahamati certifies against a
  specific ReBIT version (<https://sahamati.org.in/certification>).

## FI types available

Per Sahamati's live list: bank deposits (savings/current, recurring, term),
SEBI-regulated securities (equity shares, mutual fund units, ETFs, AIFs, REITs,
InvITs and more), GST returns (GSTR-1 and 3B), general and life insurance, and
NPS. Others (bonds, government securities, EPF, PPF) are proposed - check
availability before promising them.

## Review checklist

- [ ] The data recipient is a regulated FIU (or the app works through one).
- [ ] Consent requests the minimum FI types, date range, frequency and data life.
- [ ] All consent states handled; revocation and expiry stop fetching immediately.
- [ ] Data deleted at the end of data life; deletion logged.
- [ ] Notifications and FI data signatures verified; keys per the ReBIT spec.
- [ ] Decrypted financial data never logged; access-controlled and encrypted at rest.
- [ ] Integration certified against the current ReBIT version.
- [ ] Privacy notice and DPDP obligations covered (see `dpdp-privacy`).
