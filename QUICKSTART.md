# Quick Start Guide - AI Reporting System

Get your AI Reporting System running in 5 minutes!

## Step-by-Step Setup

### 1. Prerequisites Check

Make sure you have Docker and Docker Compose installed:
```bash
docker --version
docker-compose --version
```

If not installed, get Docker Desktop from: https://www.docker.com/products/docker-desktop

### 2. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd ai-reporting-backend

# Create environment file
cp .env.example .env
```

### 3. Configure OpenAI (Optional but Recommended)

Edit `.env` file and add your OpenAI API key:

```bash
# Open .env in your editor
nano .env  # or vim, code, etc.

# Add your OpenAI key
OPENAI_API_KEY=sk-your-actual-key-here
```

Don't have an OpenAI key? Get one at: https://platform.openai.com/api-keys

**Note:** System works without OpenAI but provides simpler summaries.

### 4. Start the System

```bash
# Start all services (PostgreSQL + Backend)
docker-compose up --build -d

# Run database migrations
docker-compose exec app alembic upgrade head

# Check if services are running
docker-compose ps
```

You should see:
- `db` container running on port 5432
- `app` container running on port 8000

### 5. Start the Frontend

```bash
# Install frontend dependencies
cd frontend
npm install

# Start development server
npm run dev
```

Frontend will start at: **http://localhost:3000**

### 6. Verify Everything Works

**Test Backend:**
```bash
# Health check
curl http://localhost:8000/health

# Should return: {"status":"ok"}
```

**Test Frontend:**
- Open http://localhost:3000 in your browser
- You should see the AI Reporting System interface

## Your First Report Analysis

### Step 1: Create KPIs

1. Click **Manage KPIs** tab
2. Add the following KPIs:

| KPI Name | Unit | Aggregation |
|----------|------|-------------|
| Revenue | USD | sum |
| Expenses | USD | sum |
| Cash Flow | USD | sum |
| Overdue Invoices | USD | sum |

Click "Create KPI" for each one.

### Step 2: Set Goals

1. Click **Set Goals** tab
2. Configure:
   - Period Type: **Monthly**
   - Period Start: **2024-10-01**
   - Period End: **2024-10-31**
3. Add KPI Targets:
   - Revenue: **1,200,000**
   - Expenses: **450,000**
   - Cash Flow: **750,000**
   - Overdue Invoices: **10,000**
4. Click "Create Goals"

### Step 3: Upload a Report

1. Click **Upload Report** tab
2. Upload the sample file: `sample_data/finance_report_october_2024.csv`
3. Wait for "Report uploaded successfully!" message
4. Note the Report ID

### Step 4: Generate AI Analysis

1. Select Goal Period: **Monthly**
2. Click **Generate AI Analysis**
3. Wait 5-10 seconds for AI to analyze
4. Review the results:
   - AI Summary with insights
   - KPI Performance table
   - Anomalies (if any)
   - Trend analysis

### Step 5: Compare with Previous Report

1. Upload another report: `sample_data/finance_report_september_2024.csv`
2. Generate analysis again
3. AI will automatically compare with the previous report!

## Testing Marketing Reports

Repeat the same process for Marketing:

**Marketing KPIs:**
- Leads Generated (count, sum)
- Ad Spend (USD, sum)
- Click Through Rate (%, avg)
- Conversions (count, sum)
- Website Visits (count, sum)
- Email Opens (count, sum)
- Social Media Engagement (count, sum)

**Sample Goals (Monthly):**
- Leads Generated: 2,000
- Ad Spend: 30,000
- Conversions: 350
- Website Visits: 100,000

**Sample Files:**
- `sample_data/marketing_report_september_2024.csv`
- `sample_data/marketing_report_october_2024.csv`

## Common Commands

### Docker Management

```bash
# View logs
docker-compose logs -f app
docker-compose logs -f db

# Restart services
docker-compose restart

# Stop all services
docker-compose down

# Stop and remove all data
docker-compose down -v
```

### Database Management

```bash
# Access PostgreSQL
docker-compose exec db psql -U postgres -d ai_reporting

# View tables
docker-compose exec db psql -U postgres -d ai_reporting -c "\dt"

# Check migration status
docker-compose exec app alembic current

# Create new migration
docker-compose exec app alembic revision --autogenerate -m "description"
```

### Frontend Development

```bash
# Install dependencies
cd frontend
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Troubleshooting

### Issue: Port 8000 or 5432 already in use

**Solution:** Stop other services using these ports or change ports in `docker-compose.yml`

```yaml
services:
  db:
    ports:
      - "5433:5432"  # Changed from 5432
  app:
    ports:
      - "8001:8000"  # Changed from 8000
```

### Issue: Frontend can't connect to backend

**Solution:** Check if backend is running and CORS is configured

```bash
# Test backend
curl http://localhost:8000/health

# Check backend logs
docker-compose logs app
```

### Issue: Database migration errors

**Solution:** Reset database and rerun migrations

```bash
# Stop services
docker-compose down -v

# Start fresh
docker-compose up -d
docker-compose exec app alembic upgrade head
```

### Issue: OpenAI errors or slow responses

**Solution:**
1. Check if `OPENAI_API_KEY` is set correctly in `.env`
2. Verify you have API credits: https://platform.openai.com/usage
3. System works without OpenAI (fallback mode)

### Issue: File upload fails

**Solution:** Check file format and permissions

```bash
# Verify upload directory exists
docker-compose exec app ls -la /app/data/uploads

# Create if missing
docker-compose exec app mkdir -p /app/data/uploads
```

## API Testing with cURL

### Create a KPI
```bash
curl -X POST http://localhost:8000/kpis \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Revenue",
    "unit": "USD",
    "aggregation": "sum"
  }'
```

### Upload a Report
```bash
curl -X POST http://localhost:8000/reports/upload \
  -H "X-API-Key: dev-key-12345" \
  -F "file=@sample_data/finance_report_october_2024.csv"
```

### Generate Analysis
```bash
curl -X POST http://localhost:8000/analyze \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "report_id": "YOUR_REPORT_ID_HERE",
    "goal_period": "monthly"
  }'
```

## Next Steps

1. **Customize KPIs**: Add your own business-specific KPIs
2. **Set Realistic Goals**: Use historical data to set achievable targets
3. **Regular Uploads**: Upload reports weekly/monthly for trend tracking
4. **Review AI Insights**: Use AI analysis to make data-driven decisions
5. **Export Results**: Copy analysis for presentations or reports

## Production Deployment

For production use:

1. **Security:**
   - Change `API_KEY` in `.env` to a secure random value
   - Use HTTPS/TLS for all connections
   - Set up proper authentication

2. **Database:**
   - Use managed PostgreSQL (AWS RDS, Google Cloud SQL, etc.)
   - Enable backups
   - Set up monitoring

3. **Deployment:**
   - Use container orchestration (Kubernetes, ECS, etc.)
   - Set up CI/CD pipeline
   - Configure environment-specific settings

4. **Monitoring:**
   - Add application monitoring (Sentry, DataDog, etc.)
   - Set up logging aggregation
   - Configure alerts

## Getting Help

**Documentation:**
- Full documentation: See `README.md`
- API documentation: http://localhost:8000/docs

**Common Issues:**
- Check the troubleshooting section above
- Review Docker logs: `docker-compose logs`
- Verify environment variables in `.env`

**Support:**
Contact the development team for assistance.

---

**Congratulations!** You're now ready to use the AI Reporting System for Finance and Marketing analytics.
