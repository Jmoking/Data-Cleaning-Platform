import React from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const API_BASE_URL = "http://127.0.0.1:8000";

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
      <h2>{title}</h2>
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
      <h2>Numeric Summary</h2>
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

function formatNumber(value) {
  if (typeof value !== "number") {
    return "-";
  }

  return Number.isInteger(value) ? value : value.toFixed(2);
}

function App() {
  const [selectedFile, setSelectedFile] = React.useState(null);
  const [result, setResult] = React.useState(null);
  const [error, setError] = React.useState("");
  const [isUploading, setIsUploading] = React.useState(false);

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
    } catch (uploadError) {
      setError(uploadError.message);
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <main className="app-shell">
      <section className="header">
        <div>
          <p className="eyebrow">Data Cleaning Platform</p>
          <h1>Upload a dataset and review the cleaning report.</h1>
        </div>
      </section>

      <section className="upload-panel">
        <form onSubmit={handleUpload}>
          <label htmlFor="file-upload">Dataset file</label>
          <div className="upload-row">
            <input
              id="file-upload"
              type="file"
              accept=".csv,.xlsx,.xls"
              onChange={(event) => setSelectedFile(event.target.files[0])}
            />
            <button type="submit" disabled={isUploading}>
              {isUploading ? "Uploading..." : "Upload"}
            </button>
          </div>
        </form>
        {error && <p className="error-message">{error}</p>}
        {result && (
          <a
            className="download-link"
            href={`${API_BASE_URL}/download/${result.cleaned_file}`}
          >
            Download cleaned file
          </a>
        )}
      </section>

      {result && (
        <div className="results-grid">
          <ProfilePanel title="Original Data" profile={result.original_profile} />
          <ProfilePanel title="Cleaned Data" profile={result.cleaned_profile} />
          <AnalysisPanel analysis={result.analysis} />
        </div>
      )}
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
