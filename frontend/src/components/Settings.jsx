import { useState } from 'react';
import { Key, Save, Eye, EyeOff } from 'lucide-react';
import { settingsAPI } from '../services/api';

function Settings() {
  const [apiKey, setApiKey] = useState(settingsAPI.getApiKey());
  const [showKey, setShowKey] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    settingsAPI.setApiKey(apiKey);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
    window.location.reload(); // Refresh to apply new key
  };

  return (
    <div className="card">
      <h2>
        <Key size={24} />
        API Settings
      </h2>

      <div className="alert alert-warning" style={{ marginBottom: '1rem' }}>
        <strong>Note:</strong> The API key must match the key configured in your backend's .env file.
        <br />
        Default key: <code>dev-key-12345</code>
      </div>

      {saved && (
        <div className="alert alert-success">
          API key saved! Refreshing to apply changes...
        </div>
      )}

      <div className="form-group">
        <label className="form-label">API Key</label>
        <div style={{ position: 'relative' }}>
          <input
            type={showKey ? 'text' : 'password'}
            className="form-input"
            placeholder="Enter your API key"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            style={{ paddingRight: '3rem' }}
          />
          <button
            type="button"
            onClick={() => setShowKey(!showKey)}
            style={{
              position: 'absolute',
              right: '0.75rem',
              top: '50%',
              transform: 'translateY(-50%)',
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              color: 'var(--text-secondary)',
              padding: '0.25rem'
            }}
          >
            {showKey ? <EyeOff size={20} /> : <Eye size={20} />}
          </button>
        </div>
      </div>

      <button
        type="button"
        className="btn btn-primary"
        onClick={handleSave}
        disabled={!apiKey}
      >
        <Save size={16} />
        Save API Key
      </button>

      <div style={{ marginTop: '2rem', padding: '1rem', background: 'var(--bg-tertiary)', borderRadius: '6px' }}>
        <h3 style={{ fontSize: '1rem', marginBottom: '0.5rem' }}>Backend Configuration</h3>
        <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
          Make sure your backend .env file has:
        </p>
        <pre style={{
          background: 'var(--bg-primary)',
          padding: '0.75rem',
          borderRadius: '4px',
          fontSize: '0.85rem',
          overflowX: 'auto'
        }}>
API_KEY=dev-key-12345
        </pre>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
          After changing the .env file, restart Docker: <code>docker-compose restart app</code>
        </p>
      </div>
    </div>
  );
}

export default Settings;
