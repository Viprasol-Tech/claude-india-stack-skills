# Contributing

Thanks for helping developers build correctly for India. Fixes, new skills, better
checklists and corrections are all welcome.

## Ways to help

- **Fix a fact.** NPCI, RBI, GST and privacy rules change often. If a rule, limit
  or header is out of date, open a PR with a link to the official source.
- **Improve a skill.** Each skill is a folder in `plugins/india-stack/skills/`
  with a `SKILL.md` (YAML frontmatter `name` + `description`, then instructions).
- **Add a skill.** Same layout. Keep `SKILL.md` under 500 lines; put long
  reference material in a separate file linked from it.
- **Improve the scripts** in `gst-invoicing/scripts`, `india-data-validation/scripts` and `upi-payments/scripts`.
  They must stay standard-library only and keep their `--self-test` passing.

## Before you open a PR

```bash
python tests/validate_repo.py
python plugins/india-stack/skills/gst-invoicing/scripts/gst.py --self-test
python plugins/india-stack/skills/india-data-validation/scripts/india_validate.py --self-test
python plugins/india-stack/skills/upi-payments/scripts/upi_link.py --self-test
```

Code samples must run as written, use test-mode keys only, and treat amounts as
Decimal/paise, never floats. Never include real Aadhaar, PAN or account numbers.

## Ground rules

- Accuracy over volume: cite official docs for platform facts.
- Regulatory content is engineering guidance, not legal or tax advice; cite the NPCI, RBI, CBIC/GSTN, UIDAI or MeitY source.
- Never include real API keys, account numbers or personal data.
