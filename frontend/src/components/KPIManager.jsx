import { useState, useEffect } from 'react';
import { Plus, TrendingUp } from 'lucide-react';
import { kpisAPI } from '../services/api';

function KPIManager({ kpis, setKpis }) {
  const [name, setName] = useState('');
  const [unit, setUnit] = useState('');
  const [aggregation, setAggregation] = useState('sum');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    loadKPIs();
  }, []);

  const loadKPIs = async () => {
    try {
      setLoading(true);
      const response = await kpisAPI.list();
      setKpis(response.data);
    } catch (err) {
      setError('Failed to load KPIs: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    try {
      setLoading(true);
      const response = await kpisAPI.create({
        name,
        unit: unit || null,
        aggregation
      });

      setKpis([...kpis, response.data]);
      setName('');
      setUnit('');
      setAggregation('sum');
      setSuccess('KPI created successfully!');
    } catch (err) {
      setError('Failed to create KPI: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="card">
        <h2>
          <Plus size={24} />
          Add New KPI
        </h2>

        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">KPI Name *</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g., Revenue, Leads Generated, Website Visits"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Unit (Optional)</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g., USD, clicks, visitors"
              value={unit}
              onChange={(e) => setUnit(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Aggregation Method *</label>
            <select
              className="form-select"
              value={aggregation}
              onChange={(e) => setAggregation(e.target.value)}
            >
              <option value="sum">Sum</option>
              <option value="avg">Average</option>
            </select>
          </div>

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Creating...' : 'Create KPI'}
          </button>
        </form>
      </div>

      <div className="card">
        <h2>
          <TrendingUp size={24} />
          Existing KPIs ({kpis.length})
        </h2>

        {loading && kpis.length === 0 ? (
          <div className="loading">
            <div className="spinner"></div>
            <p>Loading KPIs...</p>
          </div>
        ) : kpis.length === 0 ? (
          <p style={{ color: 'var(--text-secondary)' }}>
            No KPIs yet. Create your first KPI above to get started.
          </p>
        ) : (
          <div className="kpi-grid">
            {kpis.map((kpi) => (
              <div key={kpi.id} className="kpi-item">
                <div className="kpi-name">{kpi.name}</div>
                <div className="kpi-meta">
                  {kpi.unit && <span>Unit: {kpi.unit}</span>}
                  {kpi.unit && ' • '}
                  <span>Aggregation: {kpi.aggregation}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default KPIManager;
