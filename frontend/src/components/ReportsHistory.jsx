import { useState, useEffect } from 'react';
import { FileText, Calendar, Database, Eye, Clock } from 'lucide-react';
import { reportsAPI } from '../services/api';

function ReportsHistory({ onSelectReport }) {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadReports();
  }, []);

  const loadReports = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await reportsAPI.list();
      setReports(response.data);
    } catch (err) {
      setError('Failed to load reports: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatDateShort = (dateStr) => {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  return (
    <div>
      <div className="card">
        <h2>
          <FileText size={24} />
          Uploaded Reports ({reports.length})
        </h2>

        {error && <div className="alert alert-error">{error}</div>}

        {loading ? (
          <div className="loading">
            <div className="spinner"></div>
            <p>Loading reports...</p>
          </div>
        ) : reports.length === 0 ? (
          <div style={{
            textAlign: 'center',
            padding: '3rem 1rem',
            color: 'var(--text-secondary)'
          }}>
            <FileText size={48} style={{ margin: '0 auto 1rem', opacity: 0.5 }} />
            <p>No reports uploaded yet.</p>
            <p style={{ fontSize: '0.9rem', marginTop: '0.5rem' }}>
              Go to "Upload Report" tab to upload your first report.
            </p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {reports.map((report) => (
              <div
                key={report.id}
                className="report-card"
                onClick={() => onSelectReport(report.id)}
                style={{
                  padding: '1.25rem',
                  background: 'var(--bg-tertiary)',
                  border: '1px solid var(--border)',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'var(--bg-secondary)';
                  e.currentTarget.style.borderColor = 'var(--accent)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'var(--bg-tertiary)';
                  e.currentTarget.style.borderColor = 'var(--border)';
                }}
              >
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'flex-start',
                  marginBottom: '0.75rem'
                }}>
                  <div style={{ flex: 1 }}>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      marginBottom: '0.5rem'
                    }}>
                      <FileText size={20} style={{ color: 'var(--accent)' }} />
                      <span style={{
                        fontWeight: '600',
                        fontSize: '1.1rem',
                        fontFamily: 'monospace'
                      }}>
                        Report {report.id.substring(0, 8)}...
                      </span>
                      <span className={`status-badge ${report.status === 'parsed' ? 'status-above' : ''}`}>
                        {report.status}
                      </span>
                    </div>

                    <div style={{
                      display: 'flex',
                      gap: '1.5rem',
                      fontSize: '0.9rem',
                      color: 'var(--text-secondary)',
                      flexWrap: 'wrap'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                        <Clock size={16} />
                        <span>{formatDate(report.created_at)}</span>
                      </div>

                      {report.date_range && report.date_range.start && (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                          <Calendar size={16} />
                          <span>
                            {formatDateShort(report.date_range.start)} - {formatDateShort(report.date_range.end)}
                          </span>
                        </div>
                      )}

                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                        <Database size={16} />
                        <span>{report.kpi_count} KPIs</span>
                      </div>
                    </div>
                  </div>

                  <button
                    className="btn btn-primary"
                    style={{
                      padding: '0.5rem 1rem',
                      fontSize: '0.9rem'
                    }}
                    onClick={(e) => {
                      e.stopPropagation();
                      onSelectReport(report.id);
                    }}
                  >
                    <Eye size={16} />
                    View
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {reports.length > 0 && (
          <button
            type="button"
            className="btn btn-secondary"
            onClick={loadReports}
            style={{ marginTop: '1rem', width: '100%' }}
          >
            Refresh List
          </button>
        )}
      </div>
    </div>
  );
}

export default ReportsHistory;
