from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.auth import get_current_user
from app.models import RUN_STORE
from app.rules import (
    run_custom_rule,
    run_duplicate_check,
    run_null_check,
    run_schema_check,
)

router = APIRouter()


class CustomRuleModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    column: str = Field(min_length=1)
    type: str
    min: float | None = None
    max: float | None = None
    pattern: str | None = None

    @model_validator(mode="after")
    def validate_rule(self):
        if self.type not in {"range", "regex"}:
            raise ValueError("type must be 'range' or 'regex'")

        if self.type == "range":
            if self.min is None and self.max is None:
                raise ValueError("range rule requires min and/or max")
            if self.min is not None and self.max is not None and self.min > self.max:
                raise ValueError("min cannot be greater than max")

        if self.type == "regex":
            if not self.pattern:
                raise ValueError("regex rule requires pattern")

        return self


class RunChecksRequest(BaseModel):
    run_id: str
    expected_columns: list[str] | None = None
    custom_rule: CustomRuleModel | None = None


@router.post("/run")
def run_checks(req: RunChecksRequest, user=Depends(get_current_user)):
    run = RUN_STORE.get(req.run_id)
    if not run:
        raise HTTPException(status_code=404, detail="run_id not found")
    if run["user_id"] != user.get("sub"):
        raise HTTPException(status_code=403, detail="Not your run")

    df = run["df"]

    schema_result = run_schema_check(df, req.expected_columns)
    null_result = run_null_check(df)
    dup_result = run_duplicate_check(df)
    custom_result = run_custom_rule(
        df, req.custom_rule.model_dump() if req.custom_rule else None
    )

    summary = {
        "schema": schema_result["summary"],
        "nulls": null_result["summary"],
        "duplicates": dup_result["summary"],
        "custom_rule": custom_result["summary"],
    }
    issues = (
        schema_result["issues"]
        + null_result["issues"]
        + dup_result["issues"]
        + custom_result["issues"]
    )

    result = {
        "run_id": req.run_id,
        "summary": summary,
        "issue_count": len(issues),
        "issues": issues,
    }
    run["results"] = result
    return result
