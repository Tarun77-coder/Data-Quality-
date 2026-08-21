import re

import pandas as pd


def run_custom_rule(df: pd.DataFrame, rule: dict | None) -> dict:
    """Run a range or regex rule against one dataset column."""
    if not rule:
        return {"summary": {"violations": 0}, "issues": []}

    column = rule.get("column")
    rule_type = rule.get("type")

    if column not in df.columns:
        return {
            "summary": {"violations": 0},
            "issues": [{
                "row_index": None,
                "column": column,
                "check": "custom_rule",
                "detail": f"column '{column}' not found in dataset",
            }],
        }

    issues = []

    if rule_type == "range":
        min_v = rule.get("min")
        max_v = rule.get("max")
        numeric_col = pd.to_numeric(df[column], errors="coerce")

        for idx, val in numeric_col.items():
            if pd.isna(val):
                continue
            if (min_v is not None and val < min_v) or (
                max_v is not None and val > max_v
            ):
                issues.append({
                    "row_index": _safe_row_index(idx),
                    "column": column,
                    "check": "custom_rule",
                    "detail": f"value {val} outside range [{min_v}, {max_v}]",
                })

    elif rule_type == "regex":
        pattern = rule.get("pattern", "")
        try:
            compiled = re.compile(pattern)
        except re.error as exc:
            return {
                "summary": {"violations": 0},
                "issues": [{
                    "row_index": None,
                    "column": column,
                    "check": "custom_rule",
                    "detail": f"invalid regex pattern: {exc}",
                }],
            }

        for idx, val in df[column].items():
            if pd.isna(val):
                continue
            if compiled.fullmatch(str(val)) is None:
                issues.append({
                    "row_index": _safe_row_index(idx),
                    "column": column,
                    "check": "custom_rule",
                    "detail": f"value '{val}' does not match pattern '{pattern}'",
                })
    else:
        return {
            "summary": {"violations": 0},
            "issues": [{
                "row_index": None,
                "column": column,
                "check": "custom_rule",
                "detail": "unsupported rule type",
            }],
        }

    return {"summary": {"violations": len(issues)}, "issues": issues}


def _safe_row_index(index):
    try:
        return int(index)
    except (TypeError, ValueError):
        return str(index)
