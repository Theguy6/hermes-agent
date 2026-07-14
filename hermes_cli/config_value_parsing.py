"""Helpers for parsing human-entered numeric config values."""

from __future__ import annotations

import math
import re
from decimal import Decimal, InvalidOperation
from typing import Any


_RATIO_RE = re.compile(
    r"^\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*(%)?\s*$"
)
_TOKEN_RE = re.compile(
    r"^\s*([+-]?(?:(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?|"
    r"\d{1,3}(?:,\d{3})+(?:\.\d*)?|"
    r"\d{1,3}(?:_\d{3})+(?:\.\d*)?))\s*([kmgtKMGT]?)\s*(?:tokens?|tok)?\s*$"
)
_TOKEN_UNIT_MULTIPLIERS = {
    "": 1,
    "k": 1_000,
    "m": 1_000_000,
    "g": 1_000_000_000,
    "t": 1_000_000_000_000,
}


def parse_ratio_config_value(raw: Any) -> float | None:
    """Return a ratio in ``(0, 1]`` from a config scalar.

    Canonical ratios (``0.75``), percentages (``75%``), and unambiguous
    whole-number percentages (``75``) are accepted. Fractional values above
    one require a percent sign so a typo such as ``1.5`` is not treated as
    1.5 percent.
    """
    if isinstance(raw, bool) or raw is None:
        return None

    explicit_percent = False
    if isinstance(raw, (int, float)):
        value = float(raw)
    elif isinstance(raw, str):
        match = _RATIO_RE.fullmatch(raw)
        if match is None:
            return None
        value = float(match.group(1))
        explicit_percent = match.group(2) is not None
        if explicit_percent:
            value /= 100.0
    else:
        return None

    if not math.isfinite(value):
        return None
    if value > 1.0:
        if explicit_percent or not value.is_integer():
            return None
        value /= 100.0
    if value <= 0.0 or value > 1.0:
        return None
    return value


def parse_token_count_config_value(raw: Any) -> int | None:
    """Return a positive integer token count from a config scalar.

    Accepts integers, integer-valued floats, grouped integers (``272,000`` or
    ``272_000``), and decimal SI suffixes such as ``256K`` and ``1.05M``.
    Optional ``tok``/``token``/``tokens`` labels are ignored.
    """
    if isinstance(raw, bool) or raw is None:
        return None
    if isinstance(raw, int):
        return raw if raw > 0 else None
    if isinstance(raw, float):
        if not math.isfinite(raw) or raw <= 0 or not raw.is_integer():
            return None
        return int(raw)
    if not isinstance(raw, str):
        return None

    match = _TOKEN_RE.fullmatch(raw)
    if match is None:
        return None

    try:
        number = Decimal(match.group(1).replace(",", "").replace("_", ""))
    except InvalidOperation:
        return None
    if not number.is_finite() or number <= 0:
        return None

    token_count = number * _TOKEN_UNIT_MULTIPLIERS[match.group(2).lower()]
    if token_count != token_count.to_integral_value():
        return None
    return int(token_count)
