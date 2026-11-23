---
name: dpdp-privacy
description: Engineering checklist for India's Digital Personal Data Protection Act 2023 and DPDP Rules 2025 - commencement dates (Board from November 2025, consent managers from November 2026, most duties from May 2027), notice and consent design with easy withdrawal, security safeguards and one-year log retention, breach reporting to the Data Protection Board within 72 hours, the three-year erasure rule for large platforms, children's data and verifiable parental consent, Significant Data Fiduciary duties, cross-border transfers and penalties up to 250 crore. Use when building signup, consent, data retention, breach response or privacy features for users in India, or reviewing personal-data handling. Engineering guidance, not legal advice.
---

# DPDP Act 2023 and DPDP Rules 2025

India's data protection law applies to digital personal data processed in
India, and to processing abroad that offers goods or services to people in
India. Facts checked against the Act and the DPDP Rules 2025 (G.S.R. 846(E),
13 November 2025) in **November 2026**. Confirm against the official gazette and
with counsel before relying on them.

## When it applies

| Date | What starts |
|---|---|
| 13 November 2025 | Data Protection Board and its procedures (Rules 1, 2, 17-21) |
| ~13 November 2026 | Consent Manager registration (Rule 4) |
| **~13 May 2027** | Most obligations: notice, security, breach reporting, retention, children's data, rights, SDF duties, cross-border (Rules 3, 5-16, 22, 23) |

Some sources count from 14 November 2025 (publication), shifting each date by a
day. Build now: these are product changes, not a last-minute policy update.

## Notice and consent (Act s.5-6, Rule 3)

- A **stand-alone, plain-language notice** listing the personal data itemised,
  the specific purpose and the goods/services it enables, and links to withdraw
  consent, exercise rights and complain to the Board.
- Consent must be **free, specific, informed, unconditional and unambiguous**,
  given by a clear affirmative action, limited to the stated purpose. No
  pre-ticked boxes; no bundling unrelated purposes.
- **Withdrawal must be as easy as giving consent**, and processing for that
  purpose stops afterwards.
- Store each consent as a record: user, notice version, purposes, timestamp,
  channel, and withdrawal.

## Security (s.8(5), Rule 6)

Reasonable safeguards including encryption, obfuscation, masking or virtual
tokens; access controls; logging, monitoring and review; backups; security terms
in contracts with Data Processors. Keep **logs and the relevant personal data
for at least one year** for breach investigation (Rule 6(1)(e)).

## Breach response (s.8(6), Rule 7)

- Tell each affected Data Principal **without delay**: what happened, likely
  consequences, mitigation, what they can do, and a contact.
- Tell the **Data Protection Board without delay**, and send a detailed report
  **within 72 hours** of becoming aware (unless the Board allows more time).
- Engineering: detection and alerting, an incident runbook with these templates,
  and the data to identify affected users quickly.

## Retention and erasure (s.8(7), Rule 8)

- Erase personal data when the purpose is served or consent is withdrawn, unless
  law requires retention (for example tax, KYC/AML records).
- **Large platforms** - e-commerce with 2 crore+ registered users in India,
  online gaming intermediaries with 50 lakh+, social media with 2 crore+ - must
  erase data after **3 years** of user inactivity (from the last contact or the
  Rules' commencement, whichever is later), warning the user **48 hours** before.
- Implement retention as scheduled jobs driven by per-category policies, with
  legal holds.

## Rights and contact (Rules 9, 14)

Publish a contact (DPO for Significant Data Fiduciaries) and how to request
access, correction, erasure and nomination; resolve grievances within **90
days**. Build self-service export, correction and deletion where possible.

## Children and persons with disability (s.9, Rules 10-12)

- A child is anyone **under 18**. Get **verifiable consent from a parent** who is
  an identifiable adult (checked against data you hold or a virtual token, for
  example via DigiLocker). Lawful guardians of persons with disability must be
  verified too.
- No tracking, behavioural monitoring or targeted advertising directed at children
  (Act s.9(3)), subject to exemptions in the Rules.

## Significant Data Fiduciaries (s.10, Rule 13)

If notified as an SDF: a DPO based in India, an independent data auditor, a
**DPIA and audit every 12 months** with a report to the Board, due diligence on
algorithmic software, and keeping government-specified data in India.

## Cross-border transfers (s.16, Rule 15)

Allowed except to countries the government restricts by notification, subject
to its orders on foreign-state access. **Sector rules still apply**: RBI payment
data must stay in India (see `rbi-payment-rules`).

## Penalties (Schedule)

Up to **₹250 crore** for failing security safeguards; ₹200 crore for breach
notification failures or children's data violations; ₹150 crore for SDF duties;
₹50 crore for other provisions.

## Review checklist

- [ ] Data inventory: what personal data, where, why, for how long, shared with whom.
- [ ] Stand-alone notice; granular consent records with versioning; one-click withdrawal.
- [ ] Encryption at rest and in transit, access control, audit logs kept at least one year.
- [ ] Breach runbook: user and Board notices, 72-hour detailed report.
- [ ] Retention jobs per data category; 3-year inactivity erasure with 48-hour warning if in scope.
- [ ] Rights requests (access, correction, erasure, nomination) handled within 90 days.
- [ ] Age gating and verifiable parental consent for under-18 users; no targeted ads to children.
- [ ] Processor contracts include security terms; cross-border transfers checked against notifications and sector rules.
