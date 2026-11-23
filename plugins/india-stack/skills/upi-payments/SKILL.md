---
name: upi-payments
description: Build and review UPI payment flows in India - upi://pay deep links and QR payloads (pa, pn, am, tr, mode, sign), intent vs. dynamic QR vs. collect, NPCI's 2026 rules on status-check calls (first check after 60 seconds, at most 3), 15-second timeouts and peak-hour limits, UPI AutoPay mandates (pre-debit notice, AFA-free limits of 15,000 and 1 lakh), UPI Lite, refunds, failed-transaction reversal timelines, and server-side status confirmation. Includes a tested link builder and parser. Use when adding UPI checkout, QR codes or subscriptions, integrating a payment aggregator's UPI APIs, or debugging stuck or duplicate UPI payments.
allowed-tools: Bash(python ${CLAUDE_SKILL_DIR}/scripts/upi_link.py *)
---

# UPI payments

UPI is fast, but the app returning to your page proves nothing. Treat every
UPI payment as **pending until your PSP or payment aggregator confirms it
server-side**. Facts below come from NPCI's **UPI Consolidated Circular
(NPCI/UPI/CC/01, 18 September 2026)** and RBI directions, checked November
2026. Most merchants integrate through an aggregator (Razorpay, Cashfree,
PhonePe, Paytm, a bank); follow its API docs for the exact calls.

## Deep links and QR

A UPI QR code simply encodes a `upi://pay?...` link. Key parameters (UPI
Linking Specification):

| Param | Meaning |
|---|---|
| `pa` | payee VPA (required) |
| `pn` | payee name (required) |
| `am` | amount in rupees; required for dynamic links, omit to let the payer enter it |
| `cu` | currency, always `INR` |
| `tr` | your transaction/order reference (required for merchant and dynamic links) |
| `tn` | note shown to the payer |
| `mc` | 4-digit merchant category code |
| `mode` | initiation mode: 01 QR, 02 secure QR, 04 intent, 05 secure intent... |
| `url` | https link to this transaction's invoice |
| `sign` | signature over the rest of the string; must be the **last** parameter |

Encode spaces as `%20`. Signed intents (SHA256withRSA, key registered through
your acquirer) let apps skip a warning; unsigned ones show "source could not be
verified". Your aggregator usually generates the final, signed intent or QR.

```bash
U=${CLAUDE_SKILL_DIR}/scripts/upi_link.py
python $U build --pa shop@okaxis --pn "Asha Stores" --am 499 --tr ORD-1001 --mode 01
python $U parse "upi://pay?pa=shop@okaxis&pn=Asha%20Stores&am=499.00&cu=INR&tr=ORD-1001"
```

## Which flow

- **Intent** (opens the user's UPI app): required for apps and mobile web.
- **Dynamic QR** (per-order QR with amount and `tr`): for desktop web; its fields
  must not be altered.
- **Collect** requests: **P2P collect is not permitted**; merchant collect still
  exists but intent/QR are the default.
- Offer "pay by any UPI app" - it is mandatory.
- Never display a name taken from a QR as the beneficiary name; apps show the
  bank (CBS) name or a verified merchant brand.

## Status checks and timeouts (NPCI CC section 12)

- Pay request/response timeout: **15 seconds**; check-status, reversal and
  validate-address: **10 seconds**.
- **Check Transaction Status**: at most **3 times**, preferably within 2 hours,
  the first no earlier than **60 seconds** after initiation per the 2026
  consolidated circular (an April 2025 circular said 90 seconds); follow your
  PSP's exact timing.
- Errors listed as final (NPCI Annexure C) mean failed - stop checking.
- No non-user-initiated API calls in peak hours (**10:00-13:00, 17:00-21:30**);
  no bursts of batch calls.
- Prefer the aggregator's **webhook** for the final status, with check-status as
  the fallback - and reconcile daily against settlement reports.

```text
create order (pending) -> show intent / QR -> wait for webhook
  -> no webhook after 60 s? check status (max 3, spaced out)
  -> success: fulfil once (idempotent)   failure: allow retry with a NEW order/tr
  -> still pending: keep order pending; resolve from settlement file / next day
```

## Limits

- UPI Lite: up to ₹1,000 per transaction, ₹5,000 wallet balance (RBI, October 2024).
- Verified merchants (capital markets, insurance, government, tax, card bills,
  large merchants...) get enhanced per-transaction limits; check the current
  limits with your aggregator rather than hard-coding them.
- No surcharge on UPI; a convenience fee must be shown upfront and be the same
  across payment modes.
- Merchant fees (MDR) of 0.4% on some P2M UPI payments above ₹2,000 (capped at
  ₹300) were announced for October 2026, then deferred until after Diwali with no
  new date yet; check NPCI before building pricing on them.

## UPI AutoPay (subscriptions)

Per NPCI CC section 14 and RBI's **E-mandate Framework 2026** (21 April 2026):

- Mandate registration needs additional factor authentication (AFA); maximum
  validity 30 years.
- **Pre-debit notification at least 24 hours** before each debit.
- Debits up to **₹15,000** need no AFA; **₹1 lakh** for mutual funds, insurance
  premiums and credit-card bills. Above that, each debit needs AFA.
- Execution: 1 attempt plus up to 3 retries per sequence, in non-peak hours.
- Users must be able to pause and revoke (except loan/EMI mandates); mandates can
  be ported 3 times in 90 days.

## Failures and refunds

- RBI turnaround times (2019): UPI debit without credit to the beneficiary -
  auto-reversal by **T+1**; merchant payment debited without confirmation -
  reversal within **T+5**; after that the bank pays **₹100 per day**.
- Refunds go back to the original payment method through the aggregator's refund
  API; make them idempotent and reconcile them.

## Review checklist

- [ ] Order stays pending until server-side confirmation (webhook or status API) - never trust the app redirect.
- [ ] Status polling follows the 60-second / 3-attempt rule; no tight loops; no peak-hour batch calls.
- [ ] Each attempt has a unique `tr`; fulfilment is idempotent on your order id.
- [ ] Webhook signatures verified (see `claude-fintech-skills` webhook-security if installed).
- [ ] Intent on mobile, dynamic QR on desktop; amounts to 2 decimals in INR.
- [ ] AutoPay: pre-debit notice 24 h ahead, AFA above the limits, pause/revoke offered.
- [ ] No surcharge; refunds to the source; daily reconciliation with settlement files.
- [ ] Payment data stored only in India (see `rbi-payment-rules`).
