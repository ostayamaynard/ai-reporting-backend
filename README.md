# AI Reporting Agent - Finance & Marketing

AI-powered agents for automated finance and marketing reporting with Zoho integration.

## Overview

This project implements two AI agents that automate the generation and delivery of weekly and monthly reports:

1. **Finance AI Agent**: Automates financial reviews and reporting
   - Weekly summaries on revenue, expenses, cash flow, and overdue invoices
   - Monthly reports analyzing financial trends, top clients, and overall financial health
   - Visualizations of key financial metrics

2. **Marketing AI Agent**: Automates marketing performance reporting
   - Weekly campaign summaries including leads generated, ad spend, CTR, and performance
   - Monthly reports on channel performance, ROI, traffic growth, and engagement metrics
   - Visualizations of marketing metrics and campaign performance

Both agents integrate with Zoho (Finance and Marketing modules) to extract, clean, and analyze data, generating insights through AI-powered analysis and delivering reports via email and Slack.

## Features

- **Automated Data Collection**: Seamless integration with Zoho Books (Finance) and Zoho CRM/Marketing Hub
- **AI-Powered Analysis**: OpenAI-powered insights and anomaly detection
- **Rich Visualizations**: Interactive charts and graphs using Plotly
- **Flexible Delivery**: Reports delivered via email (SendGrid) and Slack
- **Scheduled Automation**: Weekly and monthly reports generated automatically
- **RESTful API**: Complete API for manual report generation and management
- **Database Tracking**: Comprehensive logging and report history

## Architecture

```
ai-reporting-backend/
├── app/
│   ├── agents/              # AI Agent implementations
│   │   ├── finance_agent.py
│   │   └── marketing_agent.py
│   ├── integrations/        # External service integrations
│   │   └── zoho.py
│   ├── routers/            # API endpoints
│   │   ├── finance.py
│   │   └── marketing.py
│   ├── services/           # Business logic services
│   │   ├── ai.py
│   │   ├── delivery.py
│   │   └── visualization.py
│   ├── models.py           # Database models
│   ├── config.py           # Configuration
│   ├── scheduler.py        # Scheduled tasks
│   └── main.py            # FastAPI application
├── migrations/             # Database migrations
├── requirements.txt        # Python dependencies
└── docker-compose.yml     # Docker setup
```

## Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL database
- Zoho API credentials
- OpenAI API key (optional, for AI summaries)
- SendGrid API key (optional, for email delivery)
- Slack Bot Token (optional, for Slack delivery)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-reporting-backend
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

5. **Start the application**
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`

### Using Docker

```bash
docker-compose up -d
```

## Configuration

Create a `.env` file based on `.env.example`:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ai_reporting_db

# API Security
API_KEY=your-secure-api-key

# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key

# Zoho Integration
ZOHO_CLIENT_ID=your-zoho-client-id
ZOHO_CLIENT_SECRET=your-zoho-client-secret
ZOHO_REFRESH_TOKEN=your-zoho-refresh-token
ZOHO_ORG_ID=your-zoho-org-id

# Email (SendGrid)
SENDGRID_API_KEY=your-sendgrid-api-key
SENDGRID_FROM_EMAIL=reports@yourcompany.com

# Slack
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_CHANNEL_FINANCE=#finance-reports
SLACK_CHANNEL_MARKETING=#marketing-reports

# Scheduling (Cron expressions)
FINANCE_WEEKLY_CRON=0 9 * * 1        # Monday 9am
FINANCE_MONTHLY_CRON=0 9 1 * *       # 1st of month 9am
MARKETING_WEEKLY_CRON=0 10 * * 1     # Monday 10am
MARKETING_MONTHLY_CRON=0 10 1 * *    # 1st of month 10am
```

## API Documentation

### Finance Agent Endpoints

#### Generate Weekly Finance Report
```bash
POST /api/v1/finance/reports/weekly
Content-Type: application/json
X-API-Key: your-api-key

{
  "deliver": true
}
```

#### Generate Monthly Finance Report
```bash
POST /api/v1/finance/reports/monthly
Content-Type: application/json
X-API-Key: your-api-key

{
  "deliver": true
}
```

#### List Finance Reports
```bash
GET /api/v1/finance/reports?limit=10&offset=0&report_type=finance_weekly
X-API-Key: your-api-key
```

#### Get Specific Finance Report
```bash
GET /api/v1/finance/reports/{report_id}
X-API-Key: your-api-key
```

### Marketing Agent Endpoints

#### Generate Weekly Marketing Report
```bash
POST /api/v1/marketing/reports/weekly
Content-Type: application/json
X-API-Key: your-api-key

{
  "deliver": true
}
```

#### Generate Monthly Marketing Report
```bash
POST /api/v1/marketing/reports/monthly
Content-Type: application/json
X-API-Key: your-api-key

{
  "deliver": true
}
```

#### List Marketing Reports
```bash
GET /api/v1/marketing/reports?limit=10&offset=0&report_type=marketing_monthly
X-API-Key: your-api-key
```

### System Endpoints

#### Health Check
```bash
GET /health
```

#### View Scheduled Jobs
```bash
GET /scheduled-jobs
```

#### Interactive API Documentation
Visit `http://localhost:8000/docs` for Swagger UI documentation.

## Zoho Integration Setup

### 1. Create Zoho OAuth App

1. Go to [Zoho API Console](https://api-console.zoho.com/)
2. Create a new "Self Client" application
3. Note your Client ID and Client Secret

### 2. Generate Refresh Token

```bash
# Step 1: Generate authorization code
https://accounts.zoho.com/oauth/v2/auth?scope=ZohoBooks.fullaccess.all,ZohoCRM.modules.ALL&client_id=YOUR_CLIENT_ID&response_type=code&access_type=offline&redirect_uri=http://localhost

# Step 2: Exchange code for refresh token
curl -X POST https://accounts.zoho.com/oauth/v2/token \
  -d "code=YOUR_AUTH_CODE" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "redirect_uri=http://localhost" \
  -d "grant_type=authorization_code"
```

### 3. Configure Environment

Add the credentials to your `.env` file:
```
ZOHO_CLIENT_ID=your_client_id
ZOHO_CLIENT_SECRET=your_client_secret
ZOHO_REFRESH_TOKEN=your_refresh_token
ZOHO_ORG_ID=your_organization_id
```

## Report Delivery Setup

### Email (SendGrid)

1. Sign up for [SendGrid](https://sendgrid.com/)
2. Create an API key
3. Verify your sender email
4. Add to `.env`:
   ```
   SENDGRID_API_KEY=your_api_key
   SENDGRID_FROM_EMAIL=reports@yourdomain.com
   ```

### Slack

1. Create a [Slack App](https://api.slack.com/apps)
2. Add OAuth permissions: `chat:write`, `files:write`
3. Install app to workspace
4. Copy Bot User OAuth Token
5. Add to `.env`:
   ```
   SLACK_BOT_TOKEN=xoxb-your-token
   SLACK_CHANNEL_FINANCE=#finance-reports
   SLACK_CHANNEL_MARKETING=#marketing-reports
   ```

## Scheduled Reports

Reports are automatically generated based on cron expressions in your configuration:

- **Finance Weekly**: Default Monday 9am
- **Finance Monthly**: Default 1st of month 9am
- **Marketing Weekly**: Default Monday 10am
- **Marketing Monthly**: Default 1st of month 10am

Modify the cron expressions in `.env` to change schedules.

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black app/
```

### Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback migration:
```bash
alembic downgrade -1
```

## Troubleshooting

### Zoho API Issues

- Ensure refresh token is valid (they expire after 3 months of inactivity)
- Check organization ID is correct
- Verify API scopes include required permissions

### Report Generation Fails

- Check Zoho credentials in database
- Review logs for specific error messages
- Ensure date ranges are valid

### Scheduled Jobs Not Running

- Verify scheduler started (check `/scheduled-jobs` endpoint)
- Check cron expressions are valid
- Review application logs

## Project Structure Details

### Models (`app/models.py`)

- `FinanceReport`: Stores finance report data and metadata
- `MarketingReport`: Stores marketing report data and metadata
- `ZohoSyncLog`: Tracks Zoho API synchronization
- `ReportDelivery`: Logs report delivery attempts

### Agents (`app/agents/`)

- `FinanceAgent`: Orchestrates finance data collection and reporting
- `MarketingAgent`: Orchestrates marketing data collection and reporting

### Services

- `visualization.py`: Creates charts and graphs
- `delivery.py`: Handles email and Slack delivery
- `ai.py`: OpenAI integration for summaries

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Create an issue on GitHub
- Contact: support@yourcompany.com

## Roadmap

### Phase 1 (Current)
- ✅ Finance AI Agent
- ✅ Marketing AI Agent
- ✅ Zoho Integration
- ✅ Email/Slack Delivery
- ✅ Scheduled Reports

### Phase 2 (Planned)
- Real-time dashboards
- Custom report templates
- Multi-currency support
- Advanced anomaly detection
- Predictive analytics

### Phase 3 (Future)
- Chatbot interface
- Additional integrations (QuickBooks, HubSpot, etc.)
- Mobile app
- Advanced data science features

## Acknowledgments

- FastAPI for the web framework
- Zoho for data integration
- OpenAI for AI capabilities
- Plotly for visualizations
