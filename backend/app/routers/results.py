import io
import json

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.auth import get_current_user
from app.models import RUN_STORE

router = APIRouter()


def _get_owned_run(run_id: str, user):
    run = RUN_STORE.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="run_id not found")
    if run["user_id"] != user.get("sub"):
        raise HTTPException(status_code=403, detail="Not your run")
    if run["results"] is None:
        raise HTTPException(
            status_code=400,
            detail="Checks have not been run for this run_id yet",
        )
    return run


@router.get("/{run_id}")
def get_results(run_id: str, user=Depends(get_current_user)):
    return _get_owned_run(run_id, user)["results"]


@router.get("/{run_id}/export")
def export_results(
    run_id: str,
    format: str = Query("json", pattern="^(csv|json)$"),
    user=Depends(get_current_user),
):
    run = _get_owned_run(run_id, user)
    results = run["results"]

    if format == "json":
        content = json.dumps(results, indent=2, ensure_ascii=False).encode("utf-8")
        return StreamingResponse(
            io.BytesIO(content),
            media_type="application/json",
            headers={
                "Content-Disposition": f'attachment; filename="results_{run_id}.json"'
            },
        )

    issues_df = pd.DataFrame(results["issues"])
    text = issues_df.to_csv(index=False)
    return StreamingResponse(
        io.BytesIO(text.encode("utf-8")),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="results_{run_id}.csv"'
        },
    )
