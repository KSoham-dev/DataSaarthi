import json
import shutil
from pathlib import Path
import uuid
import os
import pandas as pd
import seaborn as sns
from typing import Dict, Any

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


BASE_UPLOAD_DIR = Path("uploads")
MAPPING_FILE = Path("file_mapping.json")


BASE_UPLOAD_DIR.mkdir(exist_ok=True)
if not MAPPING_FILE.exists():
    MAPPING_FILE.write_text("{}")


def load_mappings() -> dict:
    """Loads the file mapping from the JSON file, handling errors."""
    try:
        with MAPPING_FILE.open("r") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def save_mappings(mappings: dict):
    """Saves the current file mapping to the JSON file."""
    with MAPPING_FILE.open("w") as f:
        json.dump(mappings, f, indent=4)


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    """
    Creates a new directory for the upload, saves the file inside it,
    and updates the mapping file.
    """
    file_id = str(uuid.uuid4())

    session_dir = BASE_UPLOAD_DIR / file_id
    session_dir.mkdir(exist_ok=True)

    destination_file_path = session_dir / file.filename

    try:

        with open(destination_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_mapping = load_mappings()
        file_mapping[file_id] = {
            "session_dir": str(session_dir),
            "original_filename": file.filename,
        }
        save_mappings(file_mapping)

    except Exception as e:

        if session_dir.exists():
            shutil.rmtree(session_dir)
        raise HTTPException(
            status_code=500, detail=f"There was an error uploading the file: {e}"
        )
    finally:
        file.file.close()

    return {"file_id": file_id}


@app.delete("/remove_file/{file_id}")
async def delete_file(file_id: str):
    """Deletes the entire directory associated with the file_id."""
    file_mapping = load_mappings()
    upload_info = file_mapping.get(file_id)

    if not upload_info:
        raise HTTPException(status_code=404, detail=f"File ID '{file_id}' not found.")

    session_dir = Path(upload_info["session_dir"])

    try:

        if session_dir.exists():
            shutil.rmtree(session_dir)

        del file_mapping[file_id]
        save_mappings(file_mapping)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred during deletion: {e}"
        )

    return {"message": f"Successfully deleted all assets for file ID '{file_id}'."}


def get_session_info(file_id: str) -> dict:
    """Helper function to get session info and handle not found errors."""
    file_mapping = load_mappings()
    session_info = file_mapping.get(file_id)
    if not session_info:
        raise HTTPException(status_code=404, detail=f"File ID '{file_id}' not found.")
    return session_info


@app.get("/get_file/{file_id}")
async def get_file(file_id: str) -> Dict[str, Any]:
    """Retrieves file details and a data sample."""
    session_info = get_session_info(file_id)
    file_path = Path(session_info["session_dir"]) / session_info["original_filename"]

    if not file_path.exists():
        raise HTTPException(
            status_code=404, detail="Original data file is missing from the server."
        )

    try:
        df = pd.read_csv(file_path)
        return {
            "file_id": file_id,
            "original_filename": session_info["original_filename"],
            "columns": df.columns.tolist(),
            "sample_data": df.head(100).to_dict(orient="records"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file data: {e}")


@app.get("/EDA/{file_id}")
async def get_eda(file_id: str) -> Dict[str, Any]:
    """Performs EDA and saves generated figures inside the session directory."""
    session_info = get_session_info(file_id)
    session_dir = Path(session_info["session_dir"])
    file_path = session_dir / session_info["original_filename"]

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Original data file is missing.")

    try:
        df = pd.read_csv(file_path)
        if df.empty:
            raise HTTPException(status_code=400, detail="The file is empty.")

        corr_plot_path = session_dir / "correlation_matrix.png"

        numeric_df = df.select_dtypes(include=[pd.np.number])
        if not numeric_df.empty:
            corr_matrix = numeric_df.corr()
            heatmap = sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f")
            heatmap.figure.tight_layout()
            heatmap.figure.savefig(corr_plot_path)
            heatmap.figure.clf()

        eda_results = {
            "file_id": file_id,
            "summary_statistics": df.describe().to_dict(),
            "figure_paths": {
                "correlation_matrix": (
                    str(corr_plot_path) if corr_plot_path.exists() else None
                ),
            },
        }
        return eda_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing EDA: {e}")


@app.get("/")
def read_root():
    return {"message": "Welcome to the DataSaarthi API"}
