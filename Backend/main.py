import json
from math import e
import shutil
from pathlib import Path
import uuid
import os
import numpy as np
import pandas as pd
import seaborn as sns
from typing import Dict, Any

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
import matplotlib.pyplot as plt

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)

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
        if file_mapping[file_id].get("assets"):
            for asset in file_mapping[file_id]["assets"]:
                asset_url = asset.get("url")
                if asset_url:
                    public_id = asset_url.split("/")[-1].split(".")[0]
                    cloudinary.uploader.destroy(public_id, invalidate=True)
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
    file_mapping = load_mappings()
    session_info = get_session_info(file_id)
    session_dir = Path(session_info["session_dir"])
    file_path = session_dir / session_info["original_filename"]

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Original data file is missing.")

    try:
        df = pd.read_csv(file_path)
        if df.empty:
            raise HTTPException(status_code=400, detail="The file is empty.")
            
        if file_mapping.get(file_id, {}).get("assets"):
            asset_urls = {
                asset["type"]: asset["url"] 
                for asset in file_mapping[file_id]["assets"] 
                if "type" in asset and "url" in asset
            }
            return {
                "file_id": file_id,
                "summary_statistics": (
                    df.describe().to_dict() 
                    if not df.select_dtypes(include=np.number).empty 
                    else None
                ),
                "cat_summary": (
                    df.select_dtypes(include=["object", "category"]).describe().to_dict()
                    if not df.select_dtypes(include=["object", "category"]).empty
                    else None
                ),
                
                "corr_figure_url": asset_urls.get("correlation_matrix"),
                "box_plot_url": asset_urls.get("box_plot"),
                "histogram_figure_url": asset_urls.get("histogram"),
                "count_plots_url": asset_urls.get("count_plot"),
            }
        else:
            pass


        eda_results = {
            "file_id": file_id,
            "summary_statistics": None,
            "corr_figure_url": None,
            "box_plot_url": None,
            "histogram_figure_url": None,
            "cat_summary": None,
            "count_plots_url": None,
        }
        file_mapping[file_id]["assets"] = []

        numeric_cols = df.select_dtypes(include=np.number).columns
        if not numeric_cols.empty:
            eda_results["summary_statistics"] = df.describe().to_dict()

            # 1. Correlation Matrix
            corr_matrix = df[numeric_cols].corr()
            plt.figure(figsize=(12, 10))
            heatmap = sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f")
            corr_plot_path = session_dir / "correlation_matrix.png"
            plt.tight_layout()
            plt.savefig(corr_plot_path)
            plt.close()
            cloudinary.uploader.upload(
                str(corr_plot_path), public_id=f"corr_matrix_{file_id}", overwrite=True
            )
            eda_results["corr_figure_url"], _ = cloudinary_url(
                f"corr_matrix_{file_id}", fetch_format="auto", quality="auto"
            )
            file_mapping[file_id]["assets"].append(
                {"url": eda_results["corr_figure_url"], "type": "correlation_matrix"}
            )

            plt.figure(figsize=(10, 6))
            sns.boxplot(data=df[numeric_cols], showfliers=False)
            plt.title("Box Plots of Numerical Features (Outliers Removed)")
            box_plot_path = session_dir / "box_plots.png"
            plt.savefig(box_plot_path)
            plt.close()
            cloudinary.uploader.upload(
                str(box_plot_path), public_id=f"box_plots_{file_id}", overwrite=True
            )
            eda_results["box_plot_url"], _ = cloudinary_url(
                f"box_plots_{file_id}", fetch_format="auto", quality="auto"
            )
            file_mapping[file_id]["assets"].append({"url": eda_results["box_plot_url"], "type": "box_plot"})

            # 3. Histograms
            n_rows = (len(numeric_cols) + 2) // 3
            fig, axes = plt.subplots(n_rows, 3, figsize=(15, n_rows * 4))
            axes = axes.flatten()
            for i, col in enumerate(numeric_cols):
                sns.histplot(data=df, x=col, kde=True, ax=axes[i])
                axes[i].set_title(f"Histogram of {col}")
            for j in range(i + 1, len(axes)):
                fig.delaxes(axes[j])
            plt.tight_layout()
            hist_plot_path = session_dir / "histograms.png"
            plt.savefig(hist_plot_path)
            plt.close()
            cloudinary.uploader.upload(
                str(hist_plot_path), public_id=f"histograms_{file_id}", overwrite=True
            )
            eda_results["histogram_figure_url"], _ = cloudinary_url(
                f"histograms_{file_id}", fetch_format="auto", quality="auto"
            )
            file_mapping[file_id]["assets"].append(
                {"url": eda_results["histogram_figure_url"], "type": "histogram"}
            )

        categorical_cols = df.select_dtypes(include=["object", "category"]).columns
        if not categorical_cols.empty:
            eda_results["cat_summary"] = df[categorical_cols].describe().to_dict()

            # 4. Count Plots
            n_rows_cat = (len(categorical_cols) + 2) // 3
            fig_cat, axes_cat = plt.subplots(
                n_rows_cat, 3, figsize=(15, n_rows_cat * 4)
            )
            axes_cat = axes_cat.flatten()
            for i, col in enumerate(categorical_cols):
                sns.countplot(data=df, x=col, ax=axes_cat[i])
                axes_cat[i].set_title(f"Count Plot of {col}")
                axes_cat[i].tick_params(axis="x", rotation=45)
            for j in range(i + 1, len(axes_cat)):
                fig_cat.delaxes(axes_cat[j])

            plt.tight_layout()
            cat_plot_path = session_dir / "categorical_plots.png"
            plt.savefig(cat_plot_path)
            plt.close()

            cloudinary.uploader.upload(
                str(cat_plot_path),
                public_id=f"categorical_plots_{file_id}",
                overwrite=True,
            )
            eda_results["count_plots_url"], _ = cloudinary_url(
                f"categorical_plots_{file_id}", fetch_format="auto", quality="auto"
            )
            file_mapping[file_id]["assets"].append(
                {"url": eda_results["count_plots_url"], "type": "count_plot"}
            )

        save_mappings(file_mapping)
        return eda_results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing EDA: {e}")


@app.get("/")
def read_root():
    return {"message": "Welcome to the DataSaarthi API"}

@app.get("/missingVals/{file_id}")
async def missingVals(file_id: str) -> Dict[str, Any]:
    """Performs EDA and saves generated figures inside the session directory."""
    # file_mapping = load_mappings()
    session_info = get_session_info(file_id)
    session_dir = Path(session_info["session_dir"])
    file_path = session_dir / session_info["original_filename"]

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Original data file is missing.")
    df = pd.read_csv(file_path)
    if df.empty:
        raise HTTPException(status_code=400, detail="The file is empty.")
    missing_values_sum = df.isna().sum().to_dict()
    if df.isna().sum().sum() == 0:
        missing_present = False
    missing_present = True
    return {
        "file_id": file_id,
        "missing_values": missing_values_sum,
        "missing_present": missing_present
    }

@app.get("/check")
def check():
    api_key = os.getenv("API_KEY")
    try:
        with open("uploads/i.png", "rb") as image_file:
            files = {
                "source": (os.path.basename("uploads/i.png"), image_file, "image/jpeg")
            }
            data = {
                "key": api_key
            }

            response = requests.post(
                "https://imgcdn.dev/api/1/upload",
                files=files,
                data=data,
            )
            response.raise_for_status
            image_url = response.text
            if not image_url:
                raise HTTPException(
                    status_code=500, detail="Image upload failed, no URL returned."
                )
    except requests.RequestException as e:
        raise HTTPException(
            status_code=500, detail=f"Error uploading image to external service: {e}"
        )
    return {"message": "API is working", "image_url": image_url}
