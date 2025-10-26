import { useState } from 'react';
import { Target, Calendar } from 'lucide-react';
import { goalsAPI } from '../services/api';

function GoalSetter({ kpis }) {
  const [periodType, setPeriodType] = useState('monthly');
  const [periodStart, setPeriodStart] = useState('');
  const [periodEnd, setPeriodEnd] = useState('');
  const [goalItems, setGoalItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const addGoalItem = () => {
    setGoalItems([
      ...goalItems,
      { kpi: kpis[0]?.name || '', target_value: 0 }
    ]);
  };

  const updateGoalItem = (index, field, value) => {
    const newItems = [...goalItems];
    newItems[index][field] = value;
    setGoalItems(newItems);
  };

  const removeGoalItem = (index) => {
    setGoalItems(goalItems.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (goalItems.length === 0) {
      setError('Please add at least one KPI goal');
      return;
    }

    try {
      setLoading(true);
      await goalsAPI.create({
        period_type: periodType,
        period_start: periodStart,
        period_end: periodEnd,
        items: goalItems
      });

      setSuccess('Goals created successfully!');
      setGoalItems([]);
      setPeriodStart('');
      setPeriodEnd('');
    } catch (err) {
      setError('Failed to create goals: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  if (kpis.length === 0) {
    return (
      <div className="card">
        <h2>
          <Target size={24} />
          Set Goals
        </h2>
        <div className="alert alert-warning">
          Please create some KPIs first before setting goals.
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <h2>
        <Target size={24} />
        Set Goals for KPIs
      </h2>

      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="form-label">
            <Calendar size={16} style={{ display: 'inline', marginRight: '0.25rem' }} />
            Period Type *
          </label>
          <select
            className="form-select"
            value={periodType}
            onChange={(e) => setPeriodType(e.target.value)}
          >
            <option value="monthly">Monthly</option>
            <option value="quarterly">Quarterly</option>
          </select>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          <div className="form-group">
            <label className="form-label">Period Start *</label>
            <input
              type="date"
              className="form-input"
              value={periodStart}
              onChange={(e) => setPeriodStart(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Period End *</label>
            <input
              type="date"
              className="form-input"
              value={periodEnd}
              onChange={(e) => setPeriodEnd(e.target.value)}
              required
            />
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">KPI Targets</label>
          {goalItems.map((item, index) => (
            <div
              key={index}
              style={{
                display: 'grid',
                gridTemplateColumns: '2fr 1fr auto',
                gap: '0.5rem',
                marginBottom: '0.5rem'
              }}
            >
              <select
                className="form-select"
                value={item.kpi}
                onChange={(e) => updateGoalItem(index, 'kpi', e.target.value)}
              >
                {kpis.map((kpi) => (
                  <option key={kpi.id} value={kpi.name}>
                    {kpi.name}
                  </option>
                ))}
              </select>

              <input
                type="number"
                className="form-input"
                placeholder="Target value"
                value={item.target_value}
                onChange={(e) =>
                  updateGoalItem(index, 'target_value', parseFloat(e.target.value) || 0)
                }
              />

              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => removeGoalItem(index)}
              >
                Remove
              </button>
            </div>
          ))}

          <button
            type="button"
            className="btn btn-secondary"
            onClick={addGoalItem}
            style={{ marginTop: '0.5rem' }}
          >
            + Add KPI Target
          </button>
        </div>

        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? 'Creating Goals...' : 'Create Goals'}
        </button>
      </form>
    </div>
  );
}

export default GoalSetter;
