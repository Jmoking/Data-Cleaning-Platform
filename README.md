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

## Run the Frontend

Install and start the React frontend:

```bash
cd frontend
npm install
npm run dev
```

Open the app:

```text
http://127.0.0.1:5173
```

Keep the backend running at the same time so the frontend can upload files to:

```text
http://127.0.0.1:8000
```

## Run as One Website

Build the frontend:

```bash
cd frontend
npm install
npm run build
cd ..
```

Start the backend:

```bash
python3 -m uvicorn backend.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

In this mode, FastAPI serves both the website and the API.

## Docker Deployment

Build the Docker image:

```bash
docker build -t data-cleaning-platform .
```

Run it locally:

```bash
docker run -p 8000:8000 data-cleaning-platform
```

Open:

```text
http://127.0.0.1:8000
```

The Docker image includes:

- React frontend build
- FastAPI backend
- Python dependencies
- R runtime for modeling scripts

## Current Cleaning Rules

After uploading a dataset, users can choose which cleaning steps to run:

- Remove duplicate rows
- Normalize column names
- Strip whitespace from text values
- Treat blank strings as missing values
- Convert numeric-looking text columns into numbers
- Fill numeric missing values with the median
- Fill text missing values with `Unknown`

Users can also skip cleaning and continue directly to modeling.

## Current Modeling Flow

After cleaning a dataset in the frontend:

1. Choose a validation method
2. Choose a regression model
3. Choose one numeric column as `Predict Y`
4. Choose one or more numeric columns as `X variables`
5. Run the model

Current validation methods:

- 80 / 20 train-test split
- K-Fold validation

Current model options:

- Pure linear regression
- Ridge regression
- Lasso regression

The model returns metrics only:

- RMSE
- MAE
- R squared
- Train row count
- Test row count

After a model is trained, the backend saves it under `storage/models/` and returns:

- Model ID
- Model parameters
- Evaluation metrics

You can then upload a new CSV or Excel file with the same X variable columns. The saved model predicts the target value, returns a preview in the frontend, and creates a downloadable CSV with a new prediction column such as:

```text
predicted_salary
```

The R script is stored at:

```text
model_engine/linear_regression.R
```

The prediction script is stored at:

```text
model_engine/predict_with_saved_model.R
```
