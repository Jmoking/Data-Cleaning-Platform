# Data Cleaning Platform

A platform for automated data cleaning and analysis.

## Tech Stack

Frontend:
- React / Next.js

Backend:
- FastAPI

Data Engine:
- pandas

## Features

- CSV upload
- Data preview
- Missing value detection
- Duplicate detection
- Automated cleaning
- Data analysis

## Setup

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

## Run the Data Engine

Process a CSV or Excel file from the project root:

```bash
python3 data_engine/main.py data_engine/dirty.csv
```

The cleaned file and JSON report are saved in:

```text
storage/outputs/
```

## Run the Backend

Start the FastAPI backend:

```bash
uvicorn backend.main:app --reload
```

Open the API docs:

```text
http://127.0.0.1:8000/docs
```

Useful endpoints:

- `GET /health`
- `POST /upload`
- `GET /download/{filename}`

## Current Cleaning Rules

- Remove duplicate rows
- Normalize column names
- Strip whitespace from text values
- Treat blank strings as missing values
- Convert numeric-looking text columns into numbers
- Fill numeric missing values with the median
- Fill text missing values with `Unknown`
