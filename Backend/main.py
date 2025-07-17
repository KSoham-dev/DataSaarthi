import json
from typing import Dict, Any
import shutil
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uuid
import os
import pandas as pd


app = FastAPI()

origins = [
    "http://localhost",
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

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

MAPPING_FILE = Path("file_mapping.json")


def load_mappings():
    """Loads the file mapping from the JSON file on startup. Handles empty or invalid files."""
    if MAPPING_FILE.exists():
        with open(MAPPING_FILE, "r") as f:
            try:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
                else:
                    return {}
            except json.JSONDecodeError:
                return {}
    return {}


def save_mappings(mappings: dict):
    """Saves the current file mapping to the JSON file."""
    with open(MAPPING_FILE, "w") as f:
        json.dump(mappings, f, indent=4)


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    """
    Accepts a file upload and saves it to the 'uploads' directory.
    The 'file' parameter name must match the key used in the frontend's FormData.
    """
    file_id = str(uuid.uuid4())
    file_ext = Path(file.filename).suffix
    unique_filename = f"{file_id}{file_ext}"
    destination_file_path = UPLOAD_DIR / unique_filename
    try:
        with open(destination_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_mapping = load_mappings()
        file_mapping[file_id] = str(destination_file_path)
        save_mappings(file_mapping)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"There was an error uploading the file: {e}"
        )
    finally:
        file.file.close()

    return {
        "file_id": str(file_id),
    }


@app.delete("/remove_file/{file_id}")
async def delete_file(file_id: str):
    file_mapping = load_mappings()
    file_path_str = file_mapping.get(file_id)
    if not file_path_str:
        raise HTTPException(
            status_code=404, detail=f"File with ID '{file_id}' not found in mapping."
        )
    try:
        print(file_path_str)
        os.remove(file_path_str)
        del file_mapping[file_id]
        save_mappings(file_mapping)
        print(file_mapping)
    except FileNotFoundError:
        del file_mapping[file_id]
        save_mappings(file_mapping)
        print(f"Info: Cleaned up stale mapping for missing file with ID '{file_id}'.")
    
    except PermissionError:
        raise HTTPException(
            status_code=500,
            detail=f"Permission denied. Could not delete file for ID '{file_id}'.",
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {e}"
        )
        
    return {"message": f"Successfully deleted file with ID '{file_id}'."}

@app.get("/get_file/{file_id}")
async def get_file(file_id: str) -> Dict[str, Any]:
    """
    Retrieves the file path for the given file ID.
    """
    file_mapping = load_mappings()
    file_path_str = file_mapping.get(file_id)
    if not file_path_str:
        raise HTTPException(
            status_code=404, detail=f"File with ID '{file_id}' not found in mapping."
        )
    
    try:
        df = pd.read_csv(file_path_str)
        return {
            "file_id": file_id,
            "file_path": str(file_path_str),
            "columns": df.columns.tolist(),
            "sample_data": df.head(100).to_dict(orient="records"),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error reading file: {e}"
        )





@app.get("/")
def read_root():
    return {"message": "Welcome to the File Upload API"}
