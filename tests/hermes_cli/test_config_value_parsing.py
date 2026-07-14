"""Unit tests for human-friendly numeric config value parsing."""

from __future__ import annotations

import math

import pytest

from hermes_cli.config_value_parsing import (
    parse_ratio_config_value,
    parse_token_count_config_value,
)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (0.75, 0.75),
        (1, 1.0),
        ("0.75", 0.75),
        (" 75% ", 0.75),
        ("75", 0.75),
        ("75.0", 0.75),
        ("75.5%", 0.755),
        ("1e2%", 1.0),
    ],
)
def test_parse_ratio_config_value_accepts_supported_forms(raw, expected):
    assert parse_ratio_config_value(raw) == pytest.approx(expected)


@pytest.mark.parametrize(
    "raw",
    [
        None,
        True,
        False,
        0,
        -0.5,
        1.5,
        101,
        math.nan,
        math.inf,
        "",
        "0%",
        "-1%",
        "101%",
        "1.5",
        "seventy-five",
        "75%%",
    ],
)
def test_parse_ratio_config_value_rejects_invalid_or_ambiguous_values(raw):
    assert parse_ratio_config_value(raw) is None


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (256_000, 256_000),
        (256_000.0, 256_000),
        ("256000", 256_000),
        ("256K", 256_000),
        (" 256 k tokens ", 256_000),
        ("1.05M", 1_050_000),
        ("1.2K", 1_200),
        ("272,000", 272_000),
        ("272_000 tok", 272_000),
        ("1e3", 1_000),
    ],
)
def test_parse_token_count_config_value_accepts_supported_forms(raw, expected):
    assert parse_token_count_config_value(raw) == expected


@pytest.mark.parametrize(
    "raw",
    [
        None,
        True,
        False,
        0,
        -1,
        1.5,
        math.nan,
        math.inf,
        "",
        "0K",
        "-1K",
        "1.2345K",  # The scaled value is not an integer token count.
        "1,2,3",
        "1_00",
        "1,000_000",
        "256KiB",
        "256KB",
        "many",
    ],
)
def test_parse_token_count_config_value_rejects_invalid_values(raw):
    assert parse_token_count_config_value(raw) is None
