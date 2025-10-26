import { useState } from 'react';
import { Upload, FileText, X } from 'lucide-react';
import { reportsAPI } from '../services/api';

function ReportUploader({ onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError(null);
      setSuccess(null);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);

    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      setFile(droppedFile);
      setError(null);
      setSuccess(null);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragging(true);
  };

  const handleDragLeave = () => {
    setDragging(false);
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setError(null);
    setSuccess(null);
    setUploading(true);

    try {
      const response = await reportsAPI.upload(file);
      const reportId = response.data.report_id;

      setSuccess(`Report uploaded successfully! ID: ${reportId}`);
      onUploadSuccess(reportId);
      setFile(null);
    } catch (err) {
      setError('Failed to upload report: ' + (err.response?.data?.detail || err.message));
    } finally {
      setUploading(false);
    }
  };

  const clearFile = () => {
    setFile(null);
    setError(null);
    setSuccess(null);
  };

  return (
    <div className="card">
      <h2>
        <Upload size={24} />
        Upload Report
      </h2>

      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      <div
        className={`file-upload-area ${dragging ? 'dragging' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => !file && document.getElementById('file-input').click()}
      >
        <Upload size={48} className="upload-icon" />
        <p style={{ color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
          {file ? 'File selected' : 'Drag and drop your report here, or click to browse'}
        </p>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
          Supported formats: CSV, TSV, Excel (.xlsx, .xls), PDF
        </p>
      </div>

      <input
        id="file-input"
        type="file"
        className="file-input"
        accept=".csv,.tsv,.xlsx,.xls,.pdf"
        onChange={handleFileChange}
      />

      {file && (
        <div className="file-info">
          <div className="file-name">
            <FileText size={20} />
            <span>{file.name}</span>
            <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
              ({(file.size / 1024).toFixed(2)} KB)
            </span>
          </div>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={clearFile}
            style={{ padding: '0.5rem' }}
          >
            <X size={16} />
          </button>
        </div>
      )}

      {file && (
        <button
          type="button"
          className="btn btn-primary"
          onClick={handleUpload}
          disabled={uploading}
          style={{ marginTop: '1rem', width: '100%' }}
        >
          {uploading ? 'Uploading...' : 'Upload Report'}
        </button>
      )}
    </div>
  );
}

export default ReportUploader;
