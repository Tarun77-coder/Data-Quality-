import pandas as pd


def run_duplicate_check(df: pd.DataFrame) -> dict:
    """Flags fully duplicate rows (all columns match)."""
    dup_mask = df.duplicated(keep="first")
    dup_indices = df.index[dup_mask].tolist()

    issues = [
        {"row_index": int(idx), "column": None, "check": "duplicates", "detail": "duplicate of an earlier row"}
        for idx in dup_indices
    ]

    return {"summary": {"count": len(dup_indices)}, "issues": issues}
