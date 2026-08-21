import pandas as pd


def run_null_check(df: pd.DataFrame) -> dict:
    """Per-column null count and percentage."""
    total_rows = len(df) or 1
    null_counts = df.isnull().sum()

    summary = {}
    issues = []
    for col, count in null_counts.items():
        pct = round((count / total_rows) * 100, 2)
        summary[col] = {"null_count": int(count), "null_pct": pct}
        if count > 0:
            null_rows = df.index[df[col].isnull()].tolist()
            for row_index in null_rows:
                issues.append({
                    "row_index": int(row_index),
                    "column": col,
                    "check": "nulls",
                    "detail": "missing value",
                })

    return {"summary": summary, "issues": issues}
