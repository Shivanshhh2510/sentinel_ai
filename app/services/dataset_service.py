import os
import pandas as pd
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.dataset import Dataset
from app.profiling.data_profiler import profile_data

UPLOAD_DIR = "uploads"


def save_dataset(file: UploadFile, user_id: int, db: Session):

    # Ensure uploads folder exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # Save file to disk
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    # Read dataset
    if file.filename.endswith(".csv"):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)

    rows, columns = df.shape

    # =========================
    # RUN DATA PROFILING
    # =========================

    profile = profile_data(df)

    # =========================
    # SAVE DATASET METADATA
    # =========================

    dataset = Dataset(
        user_id=user_id,
        name=file.filename,
        file_path=file_path,
        rows=rows,
        columns=columns
    )

    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    # =========================
    # RETURN DATASET INTELLIGENCE
    # =========================

    return {
        "dataset_id": dataset.id,
        "rows": rows,
        "columns": columns,
        "profile": profile
    }

def list_datasets(user_id: int, db: Session):

    datasets = db.query(Dataset).filter(Dataset.user_id == user_id).all()

    result = []

    for ds in datasets:
        result.append({
            "id": ds.id,
            "name": ds.name,
            "rows": ds.rows,
            "columns": ds.columns,
            "file_path": ds.file_path
        })

    return result

def get_dataset_details(dataset_id: int, db: Session):

    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()

    if not dataset:
        return None

    # Load dataset file
    file_path = dataset.file_path

    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)

    # Run profiling
    profile = profile_data(df)

    return {
        "id": dataset.id,
        "name": dataset.name,
        "rows": dataset.rows,
        "columns": dataset.columns,
        "file_path": dataset.file_path,
        "profile": profile
    }

def get_dataset_preview(dataset_id: int, db: Session, limit: int = 20):

    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()

    if not dataset:
        return None

    file_path = dataset.file_path

    # Load dataset
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)

    preview_df = df.head(limit)

    return {
        "dataset_id": dataset.id,
        "columns": preview_df.columns.tolist(),
        "rows": preview_df.to_dict(orient="records"),
        "row_count": len(df)
    }