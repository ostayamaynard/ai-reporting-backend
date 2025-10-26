import { useState } from 'react';
import { BarChart3, Target, Upload, Sparkles } from 'lucide-react';
import KPIManager from './components/KPIManager';
import GoalSetter from './components/GoalSetter';
import ReportUploader from './components/ReportUploader';
import AnalysisView from './components/AnalysisView';

function App() {
  const [activeTab, setActiveTab] = useState('upload');
  const [kpis, setKpis] = useState([]);
  const [reportId, setReportId] = useState(null);
  const [analysis, setAnalysis] = useState(null);

  const tabs = [
    { id: 'upload', label: 'Upload Report', icon: Upload },
    { id: 'kpis', label: 'Manage KPIs', icon: BarChart3 },
    { id: 'goals', label: 'Set Goals', icon: Target },
  ];

  return (
    <div className="app">
      <header className="header">
        <h1>
          <Sparkles className="header-icon" size={28} />
          AI Reporting System
        </h1>
        <nav className="nav-tabs">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
                onClick={() => setActiveTab(tab.id)}
              >
                <Icon size={16} style={{ display: 'inline', marginRight: '0.25rem' }} />
                {tab.label}
              </button>
            );
          })}
        </nav>
      </header>

      <main className="main-content">
        {activeTab === 'kpis' && (
          <KPIManager kpis={kpis} setKpis={setKpis} />
        )}

        {activeTab === 'goals' && (
          <GoalSetter kpis={kpis} />
        )}

        {activeTab === 'upload' && (
          <>
            <ReportUploader
              onUploadSuccess={(id) => {
                setReportId(id);
                setAnalysis(null);
              }}
            />

            {reportId && (
              <AnalysisView
                reportId={reportId}
                analysis={analysis}
                setAnalysis={setAnalysis}
              />
            )}
          </>
        )}
      </main>
    </div>
  );
}

export default App;
