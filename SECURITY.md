# Security policy

## Reporting a vulnerability

Please report security problems privately through
[GitHub security advisories](https://github.com/Viprasol-Tech/claude-india-stack-skills/security/advisories/new)
or by email to [support@viprasol.com](mailto:support@viprasol.com). Do not open a public issue.
We aim to reply within 3 working days.

## Scope

- The bundled scripts (`gst.py`, `inr.py`, `india_validate.py`, `upi_link.py`): they read
  command-line values or local files and print results. They make no network calls and run no
  shell commands.
- Skill instructions that could lead an assistant to weaken payment or identity
  security: storing Aadhaar or card data, skipping server-side payment confirmation.

## Keep secrets and card data out of chats

These skills never need real customer data. Never paste real Aadhaar numbers,
PAN, bank account numbers, card data, API keys or webhook secrets into an issue,
pull request or chat. Use synthetic data and sandbox keys. If a key has been
exposed, rotate it with your provider immediately.
