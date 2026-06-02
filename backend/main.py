from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import shutil
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_ENGINE_DIR = PROJECT_ROOT / "data_engine"
UPLOAD_DIR = PROJECT_ROOT / "storage" / "uploads"
OUTPUT_DIR = PROJECT_ROOT / "storage" / "outputs"
ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}

sys.path.append(str(DATA_ENGINE_DIR))

from reader import read_file
from profiler import profile_data
from cleaner import clean_data
from analyser import analyse_data

app = FastAPI()

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/")
def root():
    return {"message": "Backend is running"}


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

    # Clean data
    cleaned_df = clean_data(df)

    output_filename = "cleaned_" + filename
    output_path = OUTPUT_DIR / output_filename
    cleaned_df.to_csv(output_path, index=False)

    # Generate cleaned profile
    cleaned_profile = profile_data(cleaned_df)

    # Analyse cleaned data
    analysis = analyse_data(cleaned_df)

    return {
        "filename": file.filename,
        "original_profile": original_profile,
        "cleaned_profile": cleaned_profile,
        "analysis": analysis,
        "cleaned_file": output_filename
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
