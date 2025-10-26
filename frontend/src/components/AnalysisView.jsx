import { useState } from 'react';
import { Sparkles, User, Bot, TrendingUp, AlertTriangle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { analysisAPI } from '../services/api';

function AnalysisView({ reportId, analysis, setAnalysis }) {
  const [goalPeriod, setGoalPeriod] = useState('monthly');
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalyze = async () => {
    setError(null);
    setAnalyzing(true);

    try {
      const response = await analysisAPI.analyze({
        report_id: reportId,
        goal_period: goalPeriod
      });

      setAnalysis(response.data);
    } catch (err) {
      setError('Failed to analyze report: ' + (err.response?.data?.detail || err.message));
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <>
      <div className="card">
        <h2>
          <Sparkles size={24} />
          AI Analysis
        </h2>

        <div className="form-group">
          <label className="form-label">Goal Period</label>
          <select
            className="form-select"
            value={goalPeriod}
            onChange={(e) => setGoalPeriod(e.target.value)}
          >
            <option value="monthly">Monthly</option>
            <option value="quarterly">Quarterly</option>
          </select>
        </div>

        {error && <div className="alert alert-error">{error}</div>}

        <button
          type="button"
          className="btn btn-primary"
          onClick={handleAnalyze}
          disabled={analyzing}
          style={{ width: '100%' }}
        >
          {analyzing ? (
            <>
              <div className="spinner" style={{ width: '16px', height: '16px', borderWidth: '2px' }}></div>
              Analyzing Report...
            </>
          ) : (
            <>
              <Sparkles size={16} />
              Generate AI Analysis
            </>
          )}
        </button>
      </div>

      {analyzing && (
        <div className="loading">
          <div className="spinner"></div>
          <p>AI is analyzing your report...</p>
        </div>
      )}

      {analysis && !analyzing && (
        <div className="report-display">
          <div className="message-container">
            <div className="message user">
              <div className="message-header">
                <User size={20} />
                You
              </div>
              <p>Please analyze report ID: {reportId} for the {goalPeriod} period and compare against our goals.</p>
            </div>
          </div>

          <div className="message-container">
            <div className="message assistant">
              <div className="message-header">
                <Bot size={20} />
                AI Analysis
              </div>

              <div className="markdown-content">
                <ReactMarkdown>{analysis.summary_md}</ReactMarkdown>
              </div>

              {analysis.kpi_table && analysis.kpi_table.length > 0 && (
                <>
                  <h3 style={{ marginTop: '2rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <TrendingUp size={20} />
                    KPI Performance
                  </h3>
                  <table className="kpi-table">
                    <thead>
                      <tr>
                        <th>KPI</th>
                        <th>Target</th>
                        <th>Actual</th>
                        <th>Variance</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {analysis.kpi_table.map((row, index) => (
                        <tr key={index}>
                          <td style={{ fontWeight: '600' }}>{row.kpi}</td>
                          <td>{row.target.toLocaleString()}</td>
                          <td>{row.actual.toLocaleString()}</td>
                          <td style={{ color: row.variance >= 0 ? 'var(--success)' : 'var(--error)' }}>
                            {row.variance >= 0 ? '+' : ''}{row.variance.toLocaleString()}
                          </td>
                          <td>
                            <span className={`status-badge status-${row.status}`}>
                              {row.status === 'above' ? '✓ Above Target' : '✗ Below Target'}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </>
              )}

              {analysis.anomalies && analysis.anomalies.length > 0 && (
                <>
                  <h3 style={{ marginTop: '2rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <AlertTriangle size={20} />
                    Anomalies Detected
                  </h3>
                  <div style={{ background: 'rgba(245, 158, 11, 0.1)', padding: '1rem', borderRadius: '6px', border: '1px solid var(--warning)' }}>
                    <ul style={{ margin: 0, paddingLeft: '1.5rem' }}>
                      {analysis.anomalies.map((anomaly, index) => (
                        <li key={index} style={{ marginBottom: '0.5rem' }}>
                          <strong>{anomaly.kpi}:</strong> {anomaly.note}
                        </li>
                      ))}
                    </ul>
                  </div>
                </>
              )}

              {analysis.trend && Object.keys(analysis.trend).length > 0 && (
                <>
                  <h3 style={{ marginTop: '2rem', marginBottom: '1rem' }}>Trend Analysis</h3>
                  <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                    {Object.entries(analysis.trend).map(([kpi, trend]) => (
                      <div
                        key={kpi}
                        style={{
                          padding: '0.75rem 1rem',
                          background: 'var(--bg-tertiary)',
                          borderRadius: '6px',
                          border: '1px solid var(--border)'
                        }}
                      >
                        <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>
                          {kpi}
                        </div>
                        <div style={{ fontWeight: '600', color: trend === 'up' ? 'var(--success)' : trend === 'down' ? 'var(--error)' : 'var(--text-secondary)' }}>
                          {trend === 'up' ? '↑ Trending Up' : trend === 'down' ? '↓ Trending Down' : '→ Flat'}
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default AnalysisView;
