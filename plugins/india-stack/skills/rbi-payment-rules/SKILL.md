---
name: rbi-payment-rules
description: Engineering checklist for RBI payment regulations that shape Indian payment products - the 2025 Payment Aggregator Directions (PA-O, PA-P, PA-CB, escrow, merchant due diligence), the ban on merchants storing card data and card-on-file tokenisation, payment data localisation (stored only in India, foreign processing returned within 24 hours), the 2026 e-mandate framework, additional factor authentication rules, failed-transaction turnaround times and compensation, and no-surcharge rules. Use when designing checkout, card storage, subscriptions, refunds or data architecture for an Indian payment or commerce product. Engineering guidance, not legal advice.
---

# RBI payment rules for engineers

These rules decide architecture, not just paperwork: where data can live, what
you may store, and how refunds must work. Checked against RBI and NPCI sources
in **November 2026**. RBI updates its directions often; confirm the current
version of each before relying on it, and consult your compliance team.

## Card data: do not store it

- Since **1 October 2022**, only card issuers and card networks may store card
  data. Merchants and payment aggregators may keep only the **last four digits
  and the card issuer's name** for tracking and reconciliation (RBI circular
  RBI/2021-22/96, para 4.1-4.2, with later extensions).
- Saved cards use **card-on-file tokenisation (CoFT)**: a token unique to card +
  token requestor + merchant, created with explicit customer consent and AFA;
  customers can view and delete tokens.
- Practical result: use your aggregator's tokenised saved-card feature; never
  persist card numbers, expiry or CVV yourself (also see PCI DSS).

## Payment data localisation

- RBI circular RBI/2017-18/153 (6 April 2018): the **entire data relating to
  payment systems must be stored only in India**, including end-to-end
  transaction data. The foreign leg of a cross-border transaction may also be
  stored abroad.
- Processing abroad is allowed, but the data must be **deleted abroad and brought
  back within one business day or 24 hours, whichever is earlier** (RBI FAQ).
- Payment aggregators must comply too.
- Architecture check: primary database, replicas, backups, logs, analytics,
  error tracking and support tools holding payment data must all be in India.

## Payment Aggregator Directions (2025)

RBI Directions RBI/DPSS/2025-26/141 (15 September 2025) cover **online (PA-O),
physical (PA-P) and cross-border (PA-CB)** aggregators:

- Non-bank PAs need RBI authorisation; net worth ₹15 crore at application,
  ₹25 crore by the end of the third financial year.
- Merchant funds sit in an **escrow** account with a scheduled commercial bank
  (separate collection accounts for cross-border); no co-mingling; COD funds
  cannot pass through it.
- **Settlement timelines** must be stated transparently in the PA-merchant
  agreement.
- Merchant due diligence follows the KYC directions (CKYCR); small merchants
  (turnover up to ₹40 lakh) can be onboarded with lighter checks; ongoing
  monitoring and FIU-IND registration are required.
- Merchants must not store card credentials; PCI DSS is required; refunds go to
  the original payment method.

If you are a marketplace or platform that collects money for sellers, check
whether you need to be (or use) an authorised payment aggregator.

## Authentication and e-mandates

- **RBI Authentication Directions (25 September 2025, compliance by 1 April
  2026):** two factors, with one dynamic per transaction for most non-card-present
  payments; SMS OTP remains allowed.
- **E-mandate Framework 2026** (21 April 2026) for recurring payments on cards,
  prepaid instruments and UPI: AFA at registration; pre-debit notice at least 24
  hours before each debit; no AFA per debit up to ₹15,000 (₹1 lakh for mutual
  funds, insurance premiums and credit-card bills); customers can view, pause and
  cancel mandates.

## Failed transactions and refunds

RBI circular RBI/2019-20/67 (turnaround time harmonisation, effective 15 October
2019): failed or stuck transactions must be auto-reversed within set timelines
(for UPI: T+1 where the beneficiary was not credited, T+5 for merchant payments
without confirmation) and the bank pays **₹100 per day** of delay, without the
customer having to complain. Design refunds and reversals to be idempotent,
traceable and reconciled daily.

## Pricing rules

- No surcharge on UPI; any convenience fee must be disclosed upfront and be the
  same across payment modes (NPCI).
- Card network and RBI rules restrict passing MDR to customers; check your
  aggregator agreement.

## Review checklist

- [ ] No card numbers, expiry or CVV stored anywhere (DB, logs, analytics, support tools); only last 4 + issuer.
- [ ] Saved cards use network tokens through the aggregator.
- [ ] All payment data stores (including backups, logs, BI) hosted in India.
- [ ] Recurring payments: AFA at registration, 24-hour pre-debit notice, limits respected, cancel/pause available.
- [ ] Refunds to the original method, idempotent, reconciled; failed transactions reversed within RBI timelines.
- [ ] If you collect money on behalf of others, PA authorisation status checked.
- [ ] No surcharges; fees disclosed upfront.
