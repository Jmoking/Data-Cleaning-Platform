from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
import json
import pandas as pd
import shutil
import subprocess
import sys
import uuid

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_ENGINE_DIR = PROJECT_ROOT / "data_engine"
MODEL_ENGINE_DIR = PROJECT_ROOT / "model_engine"
FRONTEND_DIST_DIR = PROJECT_ROOT / "frontend" / "dist"
UPLOAD_DIR = PROJECT_ROOT / "storage" / "uploads"
OUTPUT_DIR = PROJECT_ROOT / "storage" / "outputs"
MODEL_DIR = PROJECT_ROOT / "storage" / "models"
PREDICTION_DIR = PROJECT_ROOT / "storage" / "predictions"
ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}

sys.path.append(str(DATA_ENGINE_DIR))

from reader import read_file
from profiler import profile_data
from cleaner import clean_data, get_cleaning_step_options
from analyser import analyse_data

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)
PREDICTION_DIR.mkdir(parents=True, exist_ok=True)


class LinearRegressionRequest(BaseModel):
    cleaned_file: str
    target_column: str
    feature_columns: list[str]
    model_type: str = "linear"
    validation_method: str = "holdout"
    k_folds: int = 5


class CleanRequest(BaseModel):
    uploaded_file: str
    steps: list[str] = []
    skip_cleaning: bool = False


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    filename = Path(file.filename).name
    file_extension = Path(filename).suffix.lower()

    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload a CSV or Excel file."
        )

    file_path = UPLOAD_DIR / filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Read uploaded file
    df = read_file(file_path)

    # Generate original profile
    original_profile = profile_data(df)

    return {
        "filename": file.filename,
        "uploaded_file": filename,
        "original_profile": original_profile,
        "cleaning_steps": get_cleaning_step_options(),
    }


@app.post("/clean")
def clean_uploaded_file(request: CleanRequest):
    safe_filename = Path(request.uploaded_file).name
    file_path = UPLOAD_DIR / safe_filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Uploaded file not found")

    df = read_file(file_path)

    if request.skip_cleaning:
        prepared_df = df.copy()
        output_filename = "prepared_" + Path(safe_filename).stem + ".csv"
        applied_steps = []
    else:
        if not request.steps:
            raise HTTPException(status_code=400, detail="Please choose at least one cleaning step or skip cleaning")

        try:
            prepared_df = clean_data(df, request.steps)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

        output_filename = "cleaned_" + Path(safe_filename).stem + ".csv"
        applied_steps = request.steps

    output_path = OUTPUT_DIR / output_filename
    prepared_df.to_csv(output_path, index=False)

    prepared_profile = profile_data(prepared_df)
    analysis = analyse_data(prepared_df)

    return {
        "filename": safe_filename,
        "cleaned_file": output_filename,
        "cleaned_profile": prepared_profile,
        "analysis": analysis,
        "applied_steps": applied_steps,
        "skipped_cleaning": request.skip_cleaning,
    }


@app.post("/model/linear-regression")
def run_linear_regression(request: LinearRegressionRequest):
    safe_filename = Path(request.cleaned_file).name
    cleaned_file_path = OUTPUT_DIR / safe_filename
    script_path = MODEL_ENGINE_DIR / "linear_regression.R"
    model_id = uuid.uuid4().hex
    model_path = MODEL_DIR / f"{model_id}.rds"

    if not cleaned_file_path.exists():
        raise HTTPException(status_code=404, detail="Cleaned file not found")

    if not request.target_column:
        raise HTTPException(status_code=400, detail="Please select a predict Y column")

    if not request.feature_columns:
        raise HTTPException(status_code=400, detail="Please select at least one X variable")

    if request.target_column in request.feature_columns:
        raise HTTPException(status_code=400, detail="Y column cannot also be an X variable")

    if request.model_type not in {"linear", "ridge", "lasso"}:
        raise HTTPException(status_code=400, detail="Model type must be linear, ridge, or lasso")

    if request.validation_method not in {"holdout", "kfold"}:
        raise HTTPException(status_code=400, detail="Validation method must be holdout or kfold")

    if request.validation_method == "kfold" and request.k_folds < 2:
        raise HTTPException(status_code=400, detail="K-Fold validation needs at least 2 folds")

    command = [
        "Rscript",
        str(script_path),
        str(cleaned_file_path),
        request.target_column,
        ",".join(request.feature_columns),
        request.model_type,
        request.validation_method,
        str(request.k_folds),
        str(model_path),
    ]

    try:
        completed_process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except FileNotFoundError as error:
        raise HTTPException(status_code=500, detail="Rscript is not installed") from error
    except subprocess.TimeoutExpired as error:
        raise HTTPException(status_code=500, detail="Model training timed out") from error

    if completed_process.returncode != 0:
        error_message = completed_process.stderr.strip() or "Model training failed"
        raise HTTPException(status_code=400, detail=error_message)

    try:
        result = json.loads(completed_process.stdout)
        result["model_id"] = model_id
        return result
    except json.JSONDecodeError as error:
        raise HTTPException(status_code=500, detail="Model script returned invalid output") from error


@app.post("/model/predict")
async def predict_with_saved_model(
    model_id: str = Form(...),
    file: UploadFile = File(...),
):
    safe_model_id = Path(model_id).name
    model_path = MODEL_DIR / f"{safe_model_id}.rds"
    script_path = MODEL_ENGINE_DIR / "predict_with_saved_model.R"

    if not model_path.exists():
        raise HTTPException(status_code=404, detail="Saved model not found")

    filename = Path(file.filename).name
    file_extension = Path(filename).suffix.lower()

    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload a CSV or Excel file."
        )

    upload_path = PREDICTION_DIR / f"{safe_model_id}_{filename}"

    with upload_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    prediction_input_df = clean_data(read_file(upload_path))
    prediction_input_path = PREDICTION_DIR / f"{safe_model_id}_prediction_input.csv"
    prediction_input_df.to_csv(prediction_input_path, index=False)

    output_filename = f"predictions_{safe_model_id}_{Path(filename).stem}.csv"
    output_path = OUTPUT_DIR / output_filename

    command = [
        "Rscript",
        str(script_path),
        str(model_path),
        str(prediction_input_path),
        str(output_path),
    ]

    try:
        completed_process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except FileNotFoundError as error:
        raise HTTPException(status_code=500, detail="Rscript is not installed") from error
    except subprocess.TimeoutExpired as error:
        raise HTTPException(status_code=500, detail="Prediction timed out") from error

    if completed_process.returncode != 0:
        error_message = completed_process.stderr.strip() or "Prediction failed"
        raise HTTPException(status_code=400, detail=error_message)

    try:
        prediction_info = json.loads(completed_process.stdout)
    except json.JSONDecodeError as error:
        raise HTTPException(status_code=500, detail="Prediction script returned invalid output") from error

    prediction_df = pd.read_csv(output_path)
    preview_df = prediction_df.head(10)
    preview_df = preview_df.where(pd.notnull(preview_df), None)

    return {
        "model_id": safe_model_id,
        "filename": filename,
        "prediction_file": output_filename,
        "prediction_column": prediction_info["prediction_column"],
        "rows": len(prediction_df),
        "preview": preview_df.to_dict(orient="records"),
    }


@app.get("/download/{filename}")
def download_file(filename: str):
    safe_filename = Path(filename).name
    file_path = OUTPUT_DIR / safe_filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=safe_filename,
        media_type="text/csv"
    )


if FRONTEND_DIST_DIR.exists():
    app.mount(
        "/assets",
        StaticFiles(directory=FRONTEND_DIST_DIR / "assets"),
        name="assets",
    )


@app.get("/{full_path:path}")
def serve_frontend(full_path: str):
    index_file = FRONTEND_DIST_DIR / "index.html"

    if not index_file.exists():
        return {"message": "Backend is running"}

    requested_file = FRONTEND_DIST_DIR / full_path

    if full_path and requested_file.is_file():
        return FileResponse(requested_file)

    return FileResponse(index_file)
