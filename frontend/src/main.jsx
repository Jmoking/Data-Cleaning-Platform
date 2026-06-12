import React from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

function StatCard({ label, value }) {
  return (
    <div className="stat-card">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function ProfilePanel({ title, profile }) {
  if (!profile) {
    return null;
  }

  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h2>{title}</h2>
          <p>{profile.columns} columns profiled</p>
        </div>
      </div>
      <div className="stat-grid">
        <StatCard label="Rows" value={profile.rows} />
        <StatCard label="Columns" value={profile.columns} />
        <StatCard label="Duplicate Rows" value={profile.duplicate_rows} />
      </div>

      <h3>Missing Values</h3>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Column</th>
              <th>Missing</th>
              <th>Type</th>
            </tr>
          </thead>
          <tbody>
            {profile.column_names.map((column) => (
              <tr key={column}>
                <td>{column}</td>
                <td>{profile.missing_values[column] ?? 0}</td>
                <td>{profile.data_types[column]}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function AnalysisPanel({ analysis }) {
  const summary = analysis?.summary_statistics;

  if (!summary) {
    return null;
  }

  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h2>Numeric Summary</h2>
          <p>{Object.keys(summary).length} numeric columns</p>
        </div>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Column</th>
              <th>Mean</th>
              <th>Median</th>
              <th>Min</th>
              <th>Max</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(summary).map(([column, stats]) => (
              <tr key={column}>
                <td>{column}</td>
                <td>{formatNumber(stats.mean)}</td>
                <td>{formatNumber(stats["50%"])}</td>
                <td>{formatNumber(stats.min)}</td>
                <td>{formatNumber(stats.max)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function ModelPanel({
  numericColumns,
  targetColumn,
  featureColumns,
  modelType,
  validationMethod,
  modelResult,
  modelError,
  predictionFile,
  predictionResult,
  predictionError,
  isTraining,
  isPredicting,
  onTargetChange,
  onFeatureToggle,
  onModelTypeChange,
  onValidationMethodChange,
  onPredictionFileChange,
  onTrain,
  onPredict,
}) {
  if (numericColumns.length === 0) {
    return null;
  }

  return (
    <section className="panel model-panel">
      <div className="panel-header">
        <div>
          <h2>Regression Model</h2>
          <p>{numericColumns.length} numeric columns available</p>
        </div>
        <span className="split-badge">
          {validationMethod === "holdout" ? "80 / 20 validation" : "5-Fold validation"}
        </span>
      </div>

      <form className="model-form" onSubmit={onTrain}>
        <div className="model-controls">
          <div>
            <label htmlFor="validation-method">Test method</label>
            <select
              id="validation-method"
              value={validationMethod}
              onChange={(event) => onValidationMethodChange(event.target.value)}
            >
              <option value="holdout">80 / 20 split</option>
              <option value="kfold">K-Fold</option>
            </select>
          </div>

          <div>
            <label htmlFor="model-type">Model</label>
            <select
              id="model-type"
              value={modelType}
              onChange={(event) => onModelTypeChange(event.target.value)}
            >
              <option value="linear">Pure linear</option>
              <option value="ridge">Ridge</option>
              <option value="lasso">Lasso</option>
            </select>
          </div>
        </div>

        <label htmlFor="target-column">Predict Y</label>
        <select
          id="target-column"
          value={targetColumn}
          onChange={(event) => onTargetChange(event.target.value)}
        >
          {numericColumns.map((column) => (
            <option key={column} value={column}>
              {column}
            </option>
          ))}
        </select>

        <fieldset>
          <legend>X variables</legend>
          <div className="checkbox-grid">
            {numericColumns
              .filter((column) => column !== targetColumn)
              .map((column) => (
                <label className="checkbox-option" key={column}>
                  <input
                    type="checkbox"
                    checked={featureColumns.includes(column)}
                    onChange={() => onFeatureToggle(column)}
                  />
                  {column}
                </label>
              ))}
          </div>
        </fieldset>

        <button type="submit" disabled={isTraining || featureColumns.length === 0}>
          {isTraining ? "Running..." : "Run model"}
        </button>
      </form>

      {modelError && <p className="error-message">{modelError}</p>}

      {modelResult && (
        <>
          <div className="model-results">
            <StatCard label="RMSE" value={formatNumber(modelResult.metrics.rmse)} />
            <StatCard label="MAE" value={formatNumber(modelResult.metrics.mae)} />
            <StatCard label="R squared" value={formatNumber(modelResult.metrics.r_squared)} />
            {modelResult.validation_method === "kfold" ? (
              <>
                <StatCard label="Folds" value={modelResult.k_folds} />
                <StatCard label="Avg test rows" value={formatNumber(modelResult.average_test_rows)} />
              </>
            ) : (
              <>
                <StatCard label="Train rows" value={modelResult.train_rows} />
                <StatCard label="Test rows" value={modelResult.test_rows} />
              </>
            )}
          </div>

          <div className="model-section">
            <h3>Model Parameters</h3>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Term</th>
                    <th>Value</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(modelResult.parameters).map(([term, value]) => (
                    <tr key={term}>
                      <td>{term}</td>
                      <td>{formatNumber(value)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="model-section">
            <h3>Predict New Data</h3>
            <form className="prediction-form" onSubmit={onPredict}>
              <input
                type="file"
                accept=".csv,.xlsx,.xls"
                onChange={(event) => onPredictionFileChange(event.target.files[0])}
              />
              <button type="submit" disabled={isPredicting || !predictionFile}>
                {isPredicting ? "Predicting..." : "Predict"}
              </button>
            </form>
            {predictionError && <p className="error-message">{predictionError}</p>}
          </div>

          {predictionResult && (
            <div className="model-section">
              <div className="panel-header compact-header">
                <div>
                  <h3>Prediction Preview</h3>
                  <p>{predictionResult.rows} rows predicted.</p>
                </div>
                <a
                  className="download-link compact-link"
                  href={`${API_BASE_URL}/download/${predictionResult.prediction_file}`}
                >
                  Download predictions
                </a>
              </div>
              <PreviewTable rows={predictionResult.preview} />
            </div>
          )}
        </>
      )}
    </section>
  );
}

function PreviewTable({ rows }) {
  if (!rows || rows.length === 0) {
    return null;
  }

  const columns = Object.keys(rows[0]);

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column}>{column}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, rowIndex) => (
            <tr key={rowIndex}>
              {columns.map((column) => (
                <td key={column}>{formatCell(row[column])}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function formatCell(value) {
  if (typeof value === "number") {
    return formatNumber(value);
  }

  return value ?? "-";
}

function formatNumber(value) {
  if (typeof value !== "number") {
    return "-";
  }

  return Number.isInteger(value) ? value : value.toFixed(2);
}

function getNumericColumns(profile) {
  if (!profile) {
    return [];
  }

  return profile.column_names.filter((column) => {
    const dataType = profile.data_types[column] || "";
    return dataType.includes("int") || dataType.includes("float");
  });
}

function App() {
  const [selectedFile, setSelectedFile] = React.useState(null);
  const [result, setResult] = React.useState(null);
  const [error, setError] = React.useState("");
  const [isUploading, setIsUploading] = React.useState(false);
  const [targetColumn, setTargetColumn] = React.useState("");
  const [featureColumns, setFeatureColumns] = React.useState([]);
  const [modelType, setModelType] = React.useState("linear");
  const [validationMethod, setValidationMethod] = React.useState("holdout");
  const [modelResult, setModelResult] = React.useState(null);
  const [modelError, setModelError] = React.useState("");
  const [isTraining, setIsTraining] = React.useState(false);
  const [predictionFile, setPredictionFile] = React.useState(null);
  const [predictionResult, setPredictionResult] = React.useState(null);
  const [predictionError, setPredictionError] = React.useState("");
  const [isPredicting, setIsPredicting] = React.useState(false);

  async function handleUpload(event) {
    event.preventDefault();

    if (!selectedFile) {
      setError("Please choose a CSV or Excel file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    setIsUploading(true);
    setError("");
    setResult(null);
    setModelResult(null);
    setModelError("");
    setPredictionFile(null);
    setPredictionResult(null);
    setPredictionError("");

    try {
      const response = await fetch(`${API_BASE_URL}/upload`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Upload failed.");
      }

      setResult(data);
      const numericColumns = getNumericColumns(data.cleaned_profile);
      setTargetColumn(numericColumns[0] || "");
      setFeatureColumns(numericColumns.slice(1));
    } catch (uploadError) {
      setError(uploadError.message);
    } finally {
      setIsUploading(false);
    }
  }

  function handleTargetChange(nextTargetColumn) {
    setTargetColumn(nextTargetColumn);
    setFeatureColumns((currentFeatureColumns) =>
      currentFeatureColumns.filter((column) => column !== nextTargetColumn)
    );
    setModelResult(null);
    setModelError("");
    setPredictionResult(null);
    setPredictionError("");
  }

  function handleFeatureToggle(column) {
    setFeatureColumns((currentFeatureColumns) =>
      currentFeatureColumns.includes(column)
        ? currentFeatureColumns.filter((featureColumn) => featureColumn !== column)
        : [...currentFeatureColumns, column]
    );
    setModelResult(null);
    setModelError("");
    setPredictionResult(null);
    setPredictionError("");
  }

  function handleModelTypeChange(nextModelType) {
    setModelType(nextModelType);
    setModelResult(null);
    setModelError("");
    setPredictionResult(null);
    setPredictionError("");
  }

  function handleValidationMethodChange(nextValidationMethod) {
    setValidationMethod(nextValidationMethod);
    setModelResult(null);
    setModelError("");
    setPredictionResult(null);
    setPredictionError("");
  }

  async function handleTrainModel(event) {
    event.preventDefault();

    if (!result) {
      setModelError("Please clean a dataset first.");
      return;
    }

    if (!targetColumn || featureColumns.length === 0) {
      setModelError("Please choose one predict Y and at least one X variable.");
      return;
    }

    setIsTraining(true);
    setModelError("");
    setModelResult(null);
    setPredictionResult(null);
    setPredictionError("");

    try {
      const response = await fetch(`${API_BASE_URL}/model/linear-regression`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          cleaned_file: result.cleaned_file,
          target_column: targetColumn,
          feature_columns: featureColumns,
          model_type: modelType,
          validation_method: validationMethod,
          k_folds: 5,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Model training failed.");
      }

      setModelResult(data);
    } catch (trainError) {
      setModelError(trainError.message);
    } finally {
      setIsTraining(false);
    }
  }

  async function handlePredict(event) {
    event.preventDefault();

    if (!modelResult?.model_id) {
      setPredictionError("Please run a model first.");
      return;
    }

    if (!predictionFile) {
      setPredictionError("Please choose a CSV or Excel file to predict.");
      return;
    }

    const formData = new FormData();
    formData.append("model_id", modelResult.model_id);
    formData.append("file", predictionFile);

    setIsPredicting(true);
    setPredictionError("");
    setPredictionResult(null);

    try {
      const response = await fetch(`${API_BASE_URL}/model/predict`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Prediction failed.");
      }

      setPredictionResult(data);
    } catch (predictError) {
      setPredictionError(predictError.message);
    } finally {
      setIsPredicting(false);
    }
  }

  const numericColumns = getNumericColumns(result?.cleaned_profile);

  return (
    <main className="app-shell">
      <nav className="brand-bar" aria-label="Actulnsight">
        <div className="brand-lockup">
          <div className="brand-mark" aria-hidden="true">
            <span>A</span>
          </div>
          <div>
            <strong>Actulnsight</strong>
            <span>Clean data and regression predictions</span>
          </div>
        </div>
      </nav>

      <section className="header">
        <div>
          <p className="eyebrow">Workspace</p>
          <h1>Prepare datasets and generate predictions.</h1>
          <p className="header-copy">
            Upload a spreadsheet, clean it, train a regression model, then export prediction results.
          </p>
        </div>
      </section>

      <section className="upload-panel">
        <div className="upload-heading">
          <div>
            <h2>Dataset intake</h2>
          </div>
          <span className="file-types">CSV / XLSX / XLS</span>
        </div>
        <form onSubmit={handleUpload}>
          <label htmlFor="file-upload">Dataset file</label>
          <div className="upload-row">
            <input
              id="file-upload"
              type="file"
              accept=".csv,.xlsx,.xls"
              onChange={(event) => setSelectedFile(event.target.files[0])}
            />
            <div className="action-row">
              <button type="submit" disabled={isUploading}>
                {isUploading ? "Cleaning..." : "Clean"}
              </button>
              <span className="info-wrap">
                <button className="info-button" type="button" aria-label="What cleaning does">
                  !
                </button>
                <ul className="tooltip" role="tooltip">
                  <li>Remove duplicate rows</li>
                  <li>Normalize column names</li>
                  <li>Trim extra spaces from text</li>
                  <li>Treat blank cells as missing</li>
                  <li>Convert numeric text into numbers</li>
                  <li>Fill missing values</li>
                </ul>
              </span>
            </div>
          </div>
        </form>
        {error && <p className="error-message">{error}</p>}
        {result && (
          <div className="file-summary">
            <div>
              <span>Cleaned file</span>
              <strong>{result.cleaned_file}</strong>
            </div>
            <a
              className="download-link compact-link"
              href={`${API_BASE_URL}/download/${result.cleaned_file}`}
            >
              Download cleaned file
            </a>
          </div>
        )}
      </section>

      {result && (
        <div className="results-grid">
          <ProfilePanel title="Original Data" profile={result.original_profile} />
          <ProfilePanel title="Cleaned Data" profile={result.cleaned_profile} />
          <AnalysisPanel analysis={result.analysis} />
          <ModelPanel
            numericColumns={numericColumns}
            targetColumn={targetColumn}
            featureColumns={featureColumns}
            modelType={modelType}
            validationMethod={validationMethod}
            modelResult={modelResult}
            modelError={modelError}
            predictionFile={predictionFile}
            predictionResult={predictionResult}
            predictionError={predictionError}
            isTraining={isTraining}
            isPredicting={isPredicting}
            onTargetChange={handleTargetChange}
            onFeatureToggle={handleFeatureToggle}
            onModelTypeChange={handleModelTypeChange}
            onValidationMethodChange={handleValidationMethodChange}
            onPredictionFileChange={setPredictionFile}
            onTrain={handleTrainModel}
            onPredict={handlePredict}
          />
        </div>
      )}
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
