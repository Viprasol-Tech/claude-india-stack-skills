---
name: gst-invoicing
description: Build GST-compliant invoicing for Indian businesses - CGST+SGST vs IGST vs UTGST from supplier state and place of supply, GST 2.0 rate slabs (5, 18, 40 percent from 22 September 2025), Rule 46 invoice fields and numbering, HSN/SAC digits by turnover, e-invoicing with IRN and signed QR via the IRP (AATO above 5 crore, 30-day reporting limit), e-way bills, rounding and round-off, lakh/crore formatting and amount in words. Includes a tested GST calculator. Use when building billing, checkout tax, invoice PDFs or GST e-invoice integrations for India, or reviewing invoice and tax code.
allowed-tools: Bash(python ${CLAUDE_SKILL_DIR}/scripts/gst.py *)
---

# GST invoicing

GST bugs show up as wrong tax type, wrong rate, numbering gaps, or invoices
the e-invoice portal (IRP) rejects. Facts below were checked in **November
2026** against CBIC, GSTN, the NIC e-invoice sandbox and GST Council records.
Rates and procedures change by notification: confirm the current position for
a specific product before going live. This is engineering guidance, not tax
advice.

## 1. Tax type

| Situation | Tax |
|---|---|
| Supplier's state = place of supply | **CGST + SGST**, each half the rate |
| Supplier in a Union territory without a legislature (Chandigarh 04, Daman & Diu 25, Dadra & Nagar Haveli and Daman & Diu 26, Lakshadweep 31, Andaman & Nicobar 35, Ladakh 38), same UT | **CGST + UTGST** |
| Supplier's state != place of supply | **IGST** |
| Exports, supplies to or by an SEZ | **Zero-rated** inter-state supplies (IGST Act s.16): either under a **Letter of Undertaking (LUT) with 0 IGST**, or with IGST paid and refunded later |

**Place of supply** is decided by the IGST Act, not by the billing address
alone: goods - where movement ends (or the bill-to party's location in
bill-to/ship-to); services to a registered recipient - the recipient's
location; unregistered - the address on record; with exceptions for immovable
property, events, transport, telecom and banking (ss.10-13). Store place of
supply as its own field on every invoice.

## 2. Rates

The 56th GST Council (3 September 2025) moved most goods to **5% and 18%**, with
**40%** for luxury and demerit goods, effective **22 September 2025**. Special
rates remain (for example 3% on gold, 0.25% on rough diamonds) and many supplies
are nil-rated or exempt. Tobacco moved to 40% (bidis 18%) from 1 February 2026.

Never hard-code a set of allowed rates. Store the rate per HSN/SAC as data with
an effective-from date, sourced from the rate notifications.

## 3. Invoice contents (CGST Rule 46)

Supplier name, address, GSTIN; **serial number**; date; recipient name, address
and GSTIN (if registered); for unregistered recipients with taxable value of
₹50,000 or more, their address and state; HSN/SAC; description, quantity, unit;
total and taxable value after discount; rate and amount of each tax; **place of
supply** with state name for inter-state supplies; delivery address if
different; whether tax is payable on **reverse charge**; signature (not needed
on e-invoices). Amount in words is convention, not a legal requirement.

**Numbering:** consecutive, up to **16 characters**, letters, digits, `-` and
`/` only, unique within each **financial year** (1 April - 31 March). Use a
database sequence per series and financial year - never `max(id) + 1` - and
never reuse a number, even for cancelled invoices. The e-invoice schema is
stricter: uppercase, and it cannot start with `0`, `/` or `-`.

**HSN digits:** aggregate turnover up to ₹5 crore - 4 digits (mandatory on B2B);
above ₹5 crore - 6 digits on all invoices; 8 digits for specified chemicals.

## 4. E-invoicing

- Mandatory when aggregate annual turnover (AATO) exceeded **₹5 crore** in any
  financial year since 2017-18 (Notification 10/2023-CT).
- The invoice JSON (schema version `1.1`, form GST INV-01) goes to an **IRP**,
  which returns the **IRN** and a **signed QR code** to print on the invoice.
- Taxpayers with AATO of **₹10 crore or more** cannot report an invoice, credit
  or debit note more than **30 days** after its date (enforced by the IRP).
- Cancel only in full, within **24 hours**; cancel any active e-way bill first.
  After that, use a credit note. A cancelled number cannot be reused.
- From **1 January 2027** (Notification 04/2026-CT) e-invoicing also covers
  self-invoices for reverse-charge supplies from unregistered persons and
  imports of services.
- Schema details that trip apps: date `dd/mm/yyyy`; `Pos` 96 for outside India;
  buyer GSTIN `URP` when unregistered; PIN 999999 for exports; amounts to 2
  decimals; `RndOffAmt` between -99.99 and 99.99.

## 5. E-way bill

Required when the consignment value exceeds **₹50,000** (Rule 138). Part A holds
invoice and goods data, Part B the vehicle. Validity: 1 day up to 200 km plus 1
day per further 200 km (20 km per day for over-dimensional cargo). Since 1
January 2025, e-way bills can only be generated for documents dated within the
last 180 days, and extensions are capped at 360 days.

## 6. Rounding

Compute each line's tax to the paise (half-up), CGST and SGST as equal halves
each rounded once. Invoices and the e-invoice schema use 2 decimals. If you
round the invoice total to the rupee, show the difference as a separate
round-off line (`RndOffAmt`). Section 170 (rounding to the rupee) applies to
amounts payable in returns.

## Calculator

```bash
python ${CLAUDE_SKILL_DIR}/scripts/gst.py calc --supplier-state 27 --pos 27 --item "Laptop,1,52000,18" --item "Mouse,2,499.50,18"
python ${CLAUDE_SKILL_DIR}/scripts/gst.py calc --supplier-state 27 --pos 29 --item "Consulting,1,100000.40,18" --round-total
python ${CLAUDE_SKILL_DIR}/scripts/gst.py calc --supplier-state 27 --pos 96 --export-or-sez --lut --item "Software export,1,500000,18"
python ${CLAUDE_SKILL_DIR}/scripts/gst.py calc --supplier-state 07 --pos 07 --items-json items.json --json
python ${CLAUDE_SKILL_DIR}/scripts/gst.py invoice-no INV/2026-27/0001
python ${CLAUDE_SKILL_DIR}/scripts/gst.py words 125000.50          # Rupees One Lakh Twenty Five Thousand and Paise Fifty Only
python ${CLAUDE_SKILL_DIR}/scripts/gst.py format 98765432.1        # ₹9,87,65,432.10
```

Item format: `description,qty,unit_price,rate[,discount]`. The place of supply
is an input: decide it with the rules in section 1 first.

## Review checklist

- [ ] Place of supply stored per invoice; tax type derived from it, not from the billing address alone.
- [ ] Rates stored per HSN/SAC with effective dates; no hard-coded rate list.
- [ ] Amounts as Decimal/paise; per-line tax rounded once; totals summed from lines.
- [ ] Invoice numbers: per-series, per-financial-year sequence, ≤16 chars, gap-free, never reused.
- [ ] HSN digits meet the turnover rule; reverse charge flagged where applicable.
- [ ] E-invoice: IRN and QR stored and printed; 30-day and 24-hour windows enforced in the workflow.
- [ ] Credit/debit notes reference the original invoice; no editing of issued invoices.
- [ ] GSTINs validated (see `india-data-validation`) and buyer state matched to the GSTIN's state code.
