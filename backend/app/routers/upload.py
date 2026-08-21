import io
import uuid
from pathlib import Path

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.auth import get_current_user
from app.models import RUN_STORE

router = APIRouter()


@router.post("")
async def upload_file(
    file: UploadFile = File(...),
    user=Depends(get_current_user),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="A file is required")

    suffix = Path(file.filename).suffix.lower()
    if suffix not in {".csv", ".json"}:
        raise HTTPException(status_code=400, detail="Only .csv and .json files are supported")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="The uploaded file is empty")

    try:
        if suffix == ".csv":
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_json(io.BytesIO(contents))
    except (ValueError, UnicodeDecodeError, pd.errors.ParserError) as exc:
        raise HTTPException(status_code=400, detail=f"Could not parse file: {exc}") from exc

    # Normalize column names while preserving the actual data values.
    df.columns = [str(column).strip() for column in df.columns]

    if df.shape[1] == 0:
        raise HTTPException(status_code=400, detail="The dataset has no columns")

    run_id = str(uuid.uuid4())
    RUN_STORE[run_id] = {
        "user_id": user.get("sub"),
        "filename": file.filename,
        "df": df,
        "results": None,
    }

    return {
        "run_id": run_id,
        "filename": file.filename,
        "columns": list(df.columns),
        "row_count": len(df),
    }
