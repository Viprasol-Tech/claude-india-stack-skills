"""Indian rupee formatting helpers: lakh/crore grouping and amounts in words.

Part of claude-india-stack-skills by Viprasol Tech Private Limited.
Imported by gst.py; standard library only.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

_ONES = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
         "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen",
         "Eighteen", "Nineteen"]
_TENS = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]


def group_indian(n: int) -> str:
    """12345678 -> '1,23,45,678' (last three digits, then pairs)."""
    s = str(abs(n))
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        pairs = []
        while len(head) > 2:
            pairs.insert(0, head[-2:])
            head = head[:-2]
        s = ",".join([head, *pairs, tail])
    return ("-" if n < 0 else "") + s


def format_inr(amount: Decimal | str | int, symbol: bool = True) -> str:
    """Decimal('1234567.5') -> '₹12,34,567.50'."""
    d = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    sign = "-" if d < 0 else ""
    rupees, paise = divmod(abs(d) * 100, 100)
    return f"{sign}{'₹' if symbol else ''}{group_indian(int(rupees))}.{int(paise):02d}"


def _below_hundred(n: int) -> str:
    if n < 20:
        return _ONES[n]
    return (_TENS[n // 10] + (" " + _ONES[n % 10] if n % 10 else "")).strip()


def _below_thousand(n: int) -> str:
    hundreds, rest = divmod(n, 100)
    parts = []
    if hundreds:
        parts.append(_ONES[hundreds] + " Hundred")
    if rest:
        parts.append(_below_hundred(rest))
    return " ".join(parts)


def words_indian(n: int) -> str:
    """Whole number in the Indian system: 12345678 -> 'One Crore Twenty Three Lakh ...'."""
    if n == 0:
        return "Zero"
    if n < 0:
        return "Minus " + words_indian(-n)
    parts = []
    crore, n = divmod(n, 10_000_000)
    if crore:
        parts.append(words_indian(crore) + " Crore")  # recursion handles 100+ crore
    lakh, n = divmod(n, 100_000)
    if lakh:
        parts.append(_below_hundred(lakh) + " Lakh")
    thousand, n = divmod(n, 1000)
    if thousand:
        parts.append(_below_hundred(thousand) + " Thousand")
    if n:
        parts.append(_below_thousand(n))
    return " ".join(parts)


def amount_in_words(amount: Decimal | str | int) -> str:
    """Invoice convention: 'Rupees One Thousand Two Hundred and Paise Fifty Only'."""
    d = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if d < 0:
        raise ValueError("amount in words is for non-negative amounts")
    rupees, paise = divmod(d * 100, 100)
    if not rupees and paise:
        return f"Paise {words_indian(int(paise))} Only"
    text = f"Rupees {words_indian(int(rupees))}"
    if paise:
        text += f" and Paise {words_indian(int(paise))}"
    return text + " Only"


def self_test() -> None:
    assert group_indian(0) == "0" and group_indian(999) == "999" and group_indian(1000) == "1,000"
    assert group_indian(123456) == "1,23,456" and group_indian(12345678) == "1,23,45,678"
    assert group_indian(1000000000) == "1,00,00,00,000" and group_indian(-1234567) == "-12,34,567"
    assert format_inr("1234567.5") == "₹12,34,567.50" and format_inr("0.005") == "₹0.01"
    assert format_inr("-99.99", symbol=False) == "-99.99"
    assert words_indian(105) == "One Hundred Five"
    assert words_indian(12345678) == "One Crore Twenty Three Lakh Forty Five Thousand Six Hundred Seventy Eight"
    assert words_indian(1_000_000_000) == "One Hundred Crore"
    assert amount_in_words("1200.50") == "Rupees One Thousand Two Hundred and Paise Fifty Only"
    assert amount_in_words(100000) == "Rupees One Lakh Only"
    assert amount_in_words("0.99") == "Paise Ninety Nine Only" and amount_in_words(0) == "Rupees Zero Only"
