import os
import shutil

from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi import Depends
from app.auth.jwt_dependency import get_current_user

from app.ingestion.csv_loader import load_csv

router = APIRouter()


@router.post("/ingest/csv")
async def ingest_csv(
    file: UploadFile = File(...),
    user=Depends(get_current_user)
):
    try:
        os.makedirs("data", exist_ok=True)
        file_path = f"data/{file.filename}"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = load_csv(file_path)

        return {
            "summary": result
        }

    except Exception as e:
        import traceback
        traceback.print_exc()

        return JSONResponse(
            status_code=500,
            content={
                "error": str(e)
            }
        )