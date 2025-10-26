import { useState, useEffect } from 'react';
import { Sparkles, User, Bot, TrendingUp, AlertTriangle, Lightbulb, Table, Send, Database } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { analysisAPI, reportsAPI } from '../services/api';

function AnalysisView({ reportId, analysis, setAnalysis }) {
  const [goalPeriod, setGoalPeriod] = useState('monthly');
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState(null);
  const [reportData, setReportData] = useState(null);
  const [loadingData, setLoadingData] = useState(false);
  const [chatMessage, setChatMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [chatting, setChatting] = useState(false);
  const [showChat, setShowChat] = useState(false);
  const [showRawData, setShowRawData] = useState(false);

  // Load report data when reportId changes
  useEffect(() => {
    if (reportId) {
      loadReportData();
    }
  }, [reportId]);

  const loadReportData = async () => {
    setLoadingData(true);
    try {
      const response = await reportsAPI.getData(reportId);
      setReportData(response.data);
    } catch (err) {
      console.error('Failed to load report data:', err);
    } finally {
      setLoadingData(false);
    }
  };

  const handleAnalyze = async () => {
    setError(null);
    setAnalyzing(true);

    try {
      const response = await analysisAPI.analyze({
        report_id: reportId,
        goal_period: goalPeriod
      });

      setAnalysis(response.data);
      setShowChat(true); // Show chat after analysis
    } catch (err) {
      setError('Failed to analyze report: ' + (err.response?.data?.detail || err.message));
    } finally {
      setAnalyzing(false);
    }
  };

  const handleSendChat = async () => {
    if (!chatMessage.trim()) return;

    const userMessage = { role: 'user', content: chatMessage };
    setChatHistory([...chatHistory, userMessage]);
    setChatMessage('');
    setChatting(true);

    try {
      const response = await analysisAPI.chat({
        report_id: reportId,
        message: chatMessage,
        conversation_history: chatHistory
      });

      const botMessage = { role: 'assistant', content: response.data.message };
      setChatHistory([...chatHistory, userMessage, botMessage]);
    } catch (err) {
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error: ' + (err.response?.data?.detail || err.message)
      };
      setChatHistory([...chatHistory, userMessage, errorMessage]);
    } finally {
      setChatting(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendChat();
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

      {/* Raw Data Table */}
      {reportData && (
        <div className="card">
          <h2 style={{ cursor: 'pointer', userSelect: 'none' }} onClick={() => setShowRawData(!showRawData)}>
            <Database size={24} />
            Report Data
            <span style={{ fontSize: '0.9rem', marginLeft: '0.5rem', color: 'var(--text-secondary)' }}>
              ({reportData.summary.total_rows} rows)
              {showRawData ? ' ▼' : ' ▶'}
            </span>
          </h2>

          {showRawData && (
            <>
              <div style={{ marginBottom: '1rem', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                Date Range: {reportData.summary.date_range.start} to {reportData.summary.date_range.end}
              </div>

              <div style={{ overflowX: 'auto', maxHeight: '400px', overflowY: 'auto' }}>
                <table className="kpi-table">
                  <thead style={{ position: 'sticky', top: 0, background: 'var(--bg-tertiary)' }}>
                    <tr>
                      <th>Date</th>
                      {reportData.kpis.map((kpi) => (
                        <th key={kpi}>{kpi}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {reportData.data.map((row, index) => (
                      <tr key={index}>
                        <td style={{ fontWeight: '600' }}>{row.date}</td>
                        {reportData.kpis.map((kpi) => (
                          <td key={kpi}>
                            {row[kpi] !== undefined ? row[kpi].toLocaleString() : '-'}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </div>
      )}

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

              {/* AI Suggestions */}
              {analysis.suggestions && analysis.suggestions.length > 0 && (
                <>
                  <h3 style={{ marginTop: '2rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Lightbulb size={20} />
                    AI Recommendations
                  </h3>
                  <div style={{ background: 'rgba(217, 119, 6, 0.1)', padding: '1rem', borderRadius: '6px', border: '1px solid var(--accent)' }}>
                    <ul style={{ margin: 0, paddingLeft: '1.5rem' }}>
                      {analysis.suggestions.map((suggestion, index) => (
                        <li key={index} style={{ marginBottom: '0.75rem', color: 'var(--text-primary)' }}>
                          {suggestion}
                        </li>
                      ))}
                    </ul>
                  </div>
                </>
              )}

              {/* KPI Performance Table */}
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

              {/* Anomalies */}
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

              {/* Trends */}
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

          {/* Chat Interface */}
          {showChat && (
            <div className="card" style={{ marginTop: '1.5rem' }}>
              <h2>
                <Bot size={24} />
                Ask Follow-up Questions
              </h2>

              <div className="chat-container" style={{ marginBottom: '1rem', maxHeight: '300px', overflowY: 'auto' }}>
                {chatHistory.map((msg, index) => (
                  <div key={index} className="message-container">
                    <div className={`message ${msg.role}`}>
                      <div className="message-header">
                        {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
                        {msg.role === 'user' ? 'You' : 'AI Assistant'}
                      </div>
                      <div className="markdown-content">
                        <ReactMarkdown>{msg.content}</ReactMarkdown>
                      </div>
                    </div>
                  </div>
                ))}
                {chatting && (
                  <div className="loading" style={{ padding: '1rem' }}>
                    <div className="spinner" style={{ width: '20px', height: '20px' }}></div>
                  </div>
                )}
              </div>

              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <input
                  type="text"
                  className="form-input"
                  placeholder="Ask about your report data..."
                  value={chatMessage}
                  onChange={(e) => setChatMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  disabled={chatting}
                  style={{ flex: 1 }}
                />
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={handleSendChat}
                  disabled={chatting || !chatMessage.trim()}
                >
                  <Send size={16} />
                </button>
              </div>

              <div style={{ marginTop: '0.75rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                Example questions: "What should I focus on first?", "Why is Revenue trending up?", "How can I improve Conversions?"
              </div>
            </div>
          )}
        </div>
      )}
    </>
  );
}

export default AnalysisView;
