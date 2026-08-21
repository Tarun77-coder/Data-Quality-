import pandas as pd

from app.rules import (
    run_custom_rule,
    run_duplicate_check,
    run_null_check,
    run_schema_check,
)


def test_schema_check_detects_missing_and_extra():
    df = pd.DataFrame({"a": [1], "c": [2]})
    result = run_schema_check(df, ["a", "b"])
    assert result["summary"]["missing"] == ["b"]
    assert result["summary"]["extra"] == ["c"]


def test_null_check_counts_correctly():
    df = pd.DataFrame({"a": [1, None, 3]})
    result = run_null_check(df)
    assert result["summary"]["a"]["null_count"] == 1


def test_duplicate_check_finds_dupes():
    df = pd.DataFrame({"a": [1, 1, 2]})
    result = run_duplicate_check(df)
    assert result["summary"]["count"] == 1
    assert result["issues"][0]["row_index"] == 1


def test_custom_rule_range_violation():
    df = pd.DataFrame({"age": [10, 150, 30]})
    rule = {"column": "age", "type": "range", "min": 0, "max": 120}
    result = run_custom_rule(df, rule)
    assert result["summary"]["violations"] == 1


def test_custom_rule_regex():
    df = pd.DataFrame({"email": ["alice@example.com", "not-an-email"]})
    rule = {
        "column": "email",
        "type": "regex",
        "pattern": r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    }
    result = run_custom_rule(df, rule)
    assert result["summary"]["violations"] == 1


def test_invalid_regex_is_reported_as_issue():
    df = pd.DataFrame({"name": ["Alice"]})
    result = run_custom_rule(df, {"column": "name", "type": "regex", "pattern": "["})
    assert result["summary"]["violations"] == 0
    assert "invalid regex pattern" in result["issues"][0]["detail"]
