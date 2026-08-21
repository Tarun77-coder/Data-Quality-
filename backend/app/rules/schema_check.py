import pandas as pd


def run_schema_check(df: pd.DataFrame, expected_columns: list[str] | None) -> dict:
    """Compares df columns against expected_columns. No-op if none provided."""
    if not expected_columns:
        return {"summary": {"missing": [], "extra": []}, "issues": []}

    actual = set(df.columns)
    expected = set(expected_columns)

    missing = sorted(expected - actual)
    extra = sorted(actual - expected)

    issues = []
    for col in missing:
        issues.append({"row_index": None, "column": col, "check": "schema", "detail": "column missing"})
    for col in extra:
        issues.append({"row_index": None, "column": col, "check": "schema", "detail": "unexpected column"})

    return {"summary": {"missing": missing, "extra": extra}, "issues": issues}
