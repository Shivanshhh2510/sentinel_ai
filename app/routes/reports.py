import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()

REPORTS_DIR = "reports"

@router.get("/download-report/{filename}")
def download_report(filename: str):

    file_path = os.path.join(REPORTS_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report not found")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/pdf"
    )
