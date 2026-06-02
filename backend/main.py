from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import shutil
import os

import sys

sys.path.append(
    os.path.abspath("../data_engine")
)

from reader import read_file
from profiler import profile_data
from cleaner import clean_data
from analyser import analyse_data

app = FastAPI()

UPLOAD_DIR = "../storage/uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def root():
    return {"message": "Backend is running"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Read uploaded file
    df = read_file(file_path)

    # Generate original profile
    original_profile = profile_data(df)

    # Clean data
    cleaned_df = clean_data(df)

    output_path = os.path.join("../storage/outputs", "cleaned_" + file.filename)
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
        "cleaned_file": output_path
}

@app.get("/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join("../storage/outputs", filename)

    if not os.path.exists(file_path):
        return {"error": "File not found"}

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="text/csv"
    )