# AI Reporting System - Finance & Marketing

A comprehensive AI-powered reporting system for automated analysis of Finance and Marketing data with intelligent insights, trend detection, and goal tracking.

## Project Overview

This system provides two AI agents:
- **Finance AI Agent**: Analyzes revenue, expenses, cash flow, and overdue invoices
- **Marketing AI Agent**: Analyzes leads, ad spend, conversions, website traffic, and engagement metrics

### Key Features

- **Upload Reports**: Support for CSV, TSV, Excel (.xlsx, .xls), and PDF files
- **KPI Management**: Define and track custom Key Performance Indicators
- **Goal Setting**: Set monthly/quarterly targets for your KPIs
- **AI Analysis**: Automated report generation with insights, comparisons, and trend detection
- **Comparison**: Compare current reports against previous periods and goals
- **Anomaly Detection**: Automatically identify significant variances (>20%)
- **Beautiful UI**: Claude-inspired interface for seamless interaction

## Tech Stack

### Backend
- **FastAPI**: Modern, fast Python web framework
- **PostgreSQL**: Robust relational database
- **SQLAlchemy**: ORM for database operations
- **OpenAI API**: AI-powered analysis (optional, has fallback)
- **Pandas**: Data processing and analysis
- **Alembic**: Database migrations

### Frontend
- **React 18**: Modern UI library
- **Vite**: Fast build tool
- **Axios**: HTTP client
- **React Markdown**: Render AI-generated markdown
- **Lucide React**: Beautiful icons

## Project Structure

```
ai-reporting-backend/
├── app/                          # Backend application
│   ├── routers/                  # API endpoints
│   │   ├── kpis.py              # KPI management
│   │   ├── goals.py             # Goal setting
│   │   ├── reports.py           # Report upload
│   │   └── analyze.py           # AI analysis
│   ├── services/                 # Business logic
│   │   ├── ai.py                # OpenAI integration
│   │   ├── parsing.py           # File parsing
│   │   └── mapping.py           # Data mapping
│   ├── models.py                # Database models
│   ├── schemas.py               # Pydantic schemas
│   ├── database.py              # DB configuration
│   ├── config.py                # Settings
│   └── main.py                  # FastAPI app
├── frontend/                     # React frontend
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── services/            # API services
│   │   ├── styles/              # CSS styles
│   │   └── App.jsx              # Main app
│   └── package.json
├── migrations/                   # Database migrations
├── sample_data/                  # Sample CSV files
├── docker-compose.yml           # Docker setup
├── Dockerfile                   # Backend Docker image
├── requirements.txt             # Python dependencies
└── .env.example                 # Environment variables template
```

## Quick Start

### Prerequisites

- Docker and Docker Compose (recommended)
- OR Python 3.11+, Node.js 18+, PostgreSQL 15+

### Option 1: Docker Setup (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-reporting-backend
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set your OpenAI API key (optional but recommended):
   ```
   OPENAI_API_KEY=your-openai-api-key-here
   ```

3. **Start the services**
   ```bash
   docker-compose up --build
   ```

4. **Run database migrations**
   ```bash
   docker-compose exec app alembic upgrade head
   ```

5. **Access the application**
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

6. **Start the frontend** (in a new terminal)
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

   Frontend will be available at: http://localhost:3000

### Option 2: Local Development Setup

1. **Setup Backend**
   ```bash
   # Install Python dependencies
   pip install -r requirements.txt

   # Start PostgreSQL (ensure it's running)
   # Update DATABASE_URL in .env to point to your local PostgreSQL

   # Run migrations
   alembic upgrade head

   # Start backend server
   uvicorn app.main:app --reload --port 8000
   ```

2. **Setup Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Usage Guide

### 1. Define Your KPIs

First, set up the Key Performance Indicators you want to track:

**For Finance:**
- Revenue
- Expenses
- Cash Flow
- Overdue Invoices

**For Marketing:**
- Leads Generated
- Ad Spend
- Click Through Rate
- Conversions
- Website Visits
- Email Opens
- Social Media Engagement

Navigate to **Manage KPIs** tab and add your KPIs with appropriate units and aggregation methods.

### 2. Set Goals

Go to **Set Goals** tab and define targets for your KPIs:

1. Select period type (Monthly or Quarterly)
2. Set start and end dates
3. Add KPI targets with specific values
4. Submit

Example Monthly Goals:
- Revenue: $1,500,000
- Expenses: $600,000
- Leads Generated: 2,500
- Conversions: 400

### 3. Upload Reports

Go to **Upload Report** tab:

1. Drag & drop or click to browse your report file
2. Supported formats: CSV, Excel, PDF
3. Click "Upload Report"
4. System will automatically:
   - Parse the file
   - Extract KPI data
   - Create/update KPIs as needed
   - Store metrics with dates

### 4. Generate AI Analysis

After uploading a report:

1. Select goal period (Monthly or Quarterly)
2. Click "Generate AI Analysis"
3. AI will:
   - Compare actuals vs targets
   - Detect anomalies (>20% variance)
   - Compare with previous reports
   - Generate insights and recommendations
   - Create visualizations

### Sample Data

Use the provided sample data files to test the system:

**Finance Reports:**
- `sample_data/finance_report_september_2024.csv`
- `sample_data/finance_report_october_2024.csv`

**Marketing Reports:**
- `sample_data/marketing_report_september_2024.csv`
- `sample_data/marketing_report_october_2024.csv`

## API Documentation

### Authentication

All API requests require an API key in the header:
```
X-API-Key: dev-key-12345
```

### Endpoints

#### KPI Management

**Create KPI**
```http
POST /kpis
Content-Type: application/json

{
  "name": "Revenue",
  "unit": "USD",
  "aggregation": "sum"
}
```

**List KPIs**
```http
GET /kpis
```

#### Goal Management

**Create Goals**
```http
POST /goals
Content-Type: application/json

{
  "period_type": "monthly",
  "period_start": "2024-10-01",
  "period_end": "2024-10-31",
  "items": [
    {
      "kpi": "Revenue",
      "target_value": 1500000,
      "unit": "USD"
    }
  ]
}
```

#### Report Management

**Upload Report**
```http
POST /reports/upload
Content-Type: multipart/form-data

file: <binary-file-data>
```

Response:
```json
{
  "report_id": "uuid-here",
  "status": "uploaded"
}
```

#### Analysis

**Generate Analysis**
```http
POST /analyze
Content-Type: application/json

{
  "report_id": "uuid-here",
  "goal_period": "monthly"
}
```

Response:
```json
{
  "summary_md": "# Analysis Summary\n...",
  "kpi_table": [
    {
      "kpi": "Revenue",
      "target": 1500000,
      "actual": 1580000,
      "variance": 80000,
      "status": "above"
    }
  ],
  "anomalies": [],
  "trend": {
    "Revenue": "up"
  }
}
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@db:5432/ai_reporting` |
| `API_KEY` | API authentication key | `dev-key-12345` |
| `OPENAI_API_KEY` | OpenAI API key (optional) | None |
| `UPLOAD_DIR` | Directory for uploaded files | `/app/data/uploads` |

### OpenAI Integration

The system can work with or without OpenAI:

- **With OpenAI**: Provides rich, contextual analysis with natural language insights
- **Without OpenAI**: Uses fallback logic to provide structured summaries

To enable OpenAI integration:
1. Get API key from https://platform.openai.com/api-keys
2. Add to `.env`: `OPENAI_API_KEY=sk-...`

## Database Schema

### Tables

- **kpis**: KPI definitions (id, name, unit, aggregation)
- **goals**: Target values for KPIs (id, kpi_id, period_type, period_start, period_end, target_value)
- **reports**: Uploaded reports (id, file_uri, source, period_start, period_end, status, created_at)
- **report_metrics**: Individual metric values (id, report_id, kpi_id, value, date)
- **analyses**: Generated analyses (id, report_id, goal_period, summary_md, comparisons_json, created_at)

## Troubleshooting

### Backend Issues

**Database connection errors:**
```bash
# Check if PostgreSQL is running
docker-compose ps

# Check logs
docker-compose logs db

# Restart services
docker-compose restart
```

**Migration errors:**
```bash
# Check migration status
docker-compose exec app alembic current

# Rerun migrations
docker-compose exec app alembic upgrade head
```

### Frontend Issues

**Port 3000 already in use:**
```bash
# Change port in vite.config.js
server: {
  port: 3001
}
```

**API connection errors:**
- Ensure backend is running on port 8000
- Check browser console for CORS errors
- Verify API_KEY matches in both frontend and backend

## Future Enhancements

### Planned Features (Currently Out of Scope)

- [ ] Real-time reporting dashboards
- [ ] Chatbot-based interactions for querying data
- [ ] Zoho API integration for automatic data sync
- [ ] Automated weekly/monthly report scheduling
- [ ] Email/Slack delivery of reports
- [ ] Third-party integrations (beyond Zoho)
- [ ] Multi-user authentication and permissions
- [ ] Custom visualization builder
- [ ] Export reports to PDF/PowerPoint

## Contributing

This is a client demo project. For modifications or features, please contact the development team.

## License

Proprietary - All rights reserved

## Support

For issues or questions, please contact the project team.
