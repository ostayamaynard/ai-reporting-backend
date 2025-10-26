# AI Reporting System - User Guide

Complete step-by-step guide to set up and use the AI Reporting System for Finance and Marketing.

## Table of Contents
1. [Initial Setup](#initial-setup)
2. [First-Time Configuration](#first-time-configuration)
3. [Creating KPIs](#creating-kpis)
4. [Setting Goals](#setting-goals)
5. [Uploading Reports](#uploading-reports)
6. [Analyzing Reports](#analyzing-reports)
7. [Viewing Report History](#viewing-report-history)
8. [Conversational AI Chat](#conversational-ai-chat)
9. [Troubleshooting](#troubleshooting)

---

## Initial Setup

### Prerequisites
- Docker Desktop installed
- Node.js 18+ installed
- Git installed
- Web browser (Chrome, Firefox, or Safari)

### Step 1: Clone the Repository

```bash
# Clone the project
git clone <repository-url>
cd ai-reporting-backend

# Switch to the correct branch
git checkout claude/finance-marketing-ai-agents-011CUVVxWTQKZajganvQ33cu
```

### Step 2: Configure Environment

```bash
# Copy the environment template
cp .env.example .env

# Edit the .env file
# For Windows: notepad .env
# For Mac/Linux: nano .env
```

**Required Configuration:**
```env
# Database (leave as is for Docker)
DATABASE_URL=postgresql://postgres:postgres@db:5432/ai_reporting

# API Security (can change for production)
API_KEY=devkey

# OpenAI (IMPORTANT: Get your key from https://platform.openai.com/api-keys)
OPENAI_API_KEY=sk-your-actual-key-here

# Upload directory (leave as is)
UPLOAD_DIR=/app/data/uploads
```

⚠️ **Important:** The system works without OpenAI but provides basic summaries. For full AI features, add your OpenAI API key.

### Step 3: Start the Backend

```bash
# Start PostgreSQL and Backend API
docker-compose up --build -d

# Wait 10 seconds for services to start
# Then run database migrations
docker-compose exec app alembic upgrade head

# Verify backend is running
curl http://localhost:8000/health
# Should return: {"status":"ok"}
```

### Step 4: Start the Frontend

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

**Frontend will be available at:** http://localhost:3000

---

## First-Time Configuration

### Configure API Key in UI

1. Open http://localhost:3000 in your browser
2. Click the **"Settings"** tab
3. Enter your API key: `devkey` (or whatever you set in .env)
4. Click **"Save API Key"**
5. Page will refresh automatically

**Troubleshooting:** If you get 401 errors, your API key doesn't match the backend. Make sure both frontend Settings and `.env` file have the same key.

---

## Creating KPIs

KPIs (Key Performance Indicators) are the metrics you want to track.

### Step 1: Navigate to Manage KPIs Tab

Click **"Manage KPIs"** in the top navigation.

### Step 2: Add Your KPIs

#### For Finance Reports:

| KPI Name | Unit | Aggregation |
|----------|------|-------------|
| Revenue | USD | sum |
| Expenses | USD | sum |
| Cash Flow | USD | sum |
| Overdue Invoices | USD | sum |
| Profit Margin | % | avg |
| Client Count | count | sum |

#### For Marketing Reports:

| KPI Name | Unit | Aggregation |
|----------|------|-------------|
| Leads Generated | count | sum |
| Ad Spend | USD | sum |
| Click Through Rate | % | avg |
| Conversions | count | sum |
| Website Visits | count | sum |
| Email Opens | count | sum |
| Social Media Engagement | count | sum |
| Cost Per Lead | USD | avg |
| ROI | % | avg |

### Step 3: Create Each KPI

1. Fill in **KPI Name** (e.g., "Revenue")
2. Fill in **Unit** (e.g., "USD") - Optional
3. Select **Aggregation Method**:
   - **Sum**: For totals (Revenue, Leads, Visits)
   - **Average**: For rates and percentages (CTR, ROI)
4. Click **"Create KPI"**
5. Repeat for all KPIs

**Note:** You can also skip this step - KPIs will be auto-created when you upload reports!

---

## Setting Goals

Goals are your targets for each KPI.

### Step 1: Navigate to Set Goals Tab

Click **"Set Goals"** in the top navigation.

### Step 2: Choose Period Type

- **Monthly**: For monthly targets
- **Quarterly**: For quarterly targets

### Step 3: Set Date Range

Example for October 2024 monthly goals:
- **Period Start**: 2024-10-01
- **Period End**: 2024-10-31

### Step 4: Add KPI Targets

Click **"+ Add KPI Target"** for each goal:

#### Example Finance Goals (Monthly):

| KPI | Target Value |
|-----|--------------|
| Revenue | 1,200,000 |
| Expenses | 450,000 |
| Cash Flow | 750,000 |
| Overdue Invoices | 10,000 |

#### Example Marketing Goals (Monthly):

| KPI | Target Value |
|-----|--------------|
| Leads Generated | 2,000 |
| Ad Spend | 30,000 |
| Conversions | 350 |
| Website Visits | 100,000 |

### Step 5: Create Goals

Click **"Create Goals"** button at the bottom.

---

## Uploading Reports

### Step 1: Navigate to Upload Report Tab

Click **"Upload Report"** in the top navigation.

### Step 2: Prepare Your Report File

**Supported Formats:**
- CSV (.csv)
- TSV (.tsv)
- Excel (.xlsx, .xls)
- PDF (.pdf)

**Required Format:**

Your file must have:
- A **header row** with column names
- A **Date column** (first column recommended)
- **KPI columns** with numeric values

**Example CSV Format:**
```csv
Date,Revenue,Expenses,Cash Flow,Overdue Invoices
2024-10-01,50000,15000,35000,2500
2024-10-02,52000,16000,36000,2500
2024-10-03,48000,16500,31500,2000
```

### Step 3: Upload the File

**Option A: Drag and Drop**
1. Drag your file into the upload area
2. File will be highlighted when ready

**Option B: Click to Browse**
1. Click anywhere in the upload area
2. Select your file from the file picker

### Step 4: Confirm Upload

1. You'll see the file name and size
2. Click **"Upload Report"** button
3. Wait for "Report uploaded successfully!" message
4. Note the Report ID shown

**What Happens Next:**
- Report is parsed automatically
- KPIs are extracted (or created if new)
- Data is stored by date
- Report appears in history

---

## Analyzing Reports

### Step 1: Ensure Goals Are Set

Make sure you've set goals for the period you want to analyze (see [Setting Goals](#setting-goals)).

### Step 2: Select Goal Period

After uploading a report, you'll see the **"AI Analysis"** section:
- Choose **Monthly** or **Quarterly**
- Must match the period type of your goals

### Step 3: Generate Analysis

Click **"Generate AI Analysis"** button.

**What You'll See:**

#### 1. Report Data Table (Collapsible)
- Click to expand/collapse
- Shows all raw data from your upload
- Organized by date
- All KPIs visible

#### 2. AI Summary
- Executive summary of performance
- "On track / Mixed / Off track" verdict
- Key highlights and lowlights

#### 3. AI Recommendations
- 3-5 specific, actionable suggestions
- Prioritized by importance
- Based on your actual data
- Example: "Reduce expenses by 15% to meet quarterly target"

#### 4. KPI Performance Table
- Target vs Actual comparison
- Variance (difference)
- Status badges (Above/Below)
- Color-coded

#### 5. Anomalies Detected
- KPIs with >20% variance
- Highlighted in yellow/orange
- Requires attention

#### 6. Trend Analysis
- Up/Down/Flat indicators
- Visual arrows
- Per KPI

### Step 4: Review the Analysis

Take time to:
- Read the AI summary
- Review recommendations
- Check which KPIs need attention
- Note any anomalies

---

## Viewing Report History

### Step 1: Navigate to Reports History Tab

Click **"Reports History"** in the top navigation.

### Step 2: Browse Your Reports

You'll see all uploaded reports with:
- Report ID (shortened)
- Upload timestamp
- Date range covered
- Number of KPIs
- Status badge

### Step 3: Select a Report

**Option A: Click the Card**
- Click anywhere on the report card

**Option B: Click View Button**
- Click the **"View"** button on the right

**What Happens:**
- System switches to "Upload Report" tab
- Selected report loads automatically
- You can now analyze it

### Step 4: Analyze Historical Reports

1. Generate analysis for old reports
2. Compare different periods
3. See how performance changed over time

### Step 5: Compare Reports

To compare two reports:
1. View Report A → Generate analysis → Note insights
2. Go to Reports History
3. View Report B → Generate analysis → Compare
4. The AI will automatically mention comparisons to previous reports!

---

## Conversational AI Chat

After generating an analysis, you can ask follow-up questions!

### Step 1: Locate the Chat Box

After analysis is generated, scroll down to find:
**"Ask Follow-up Questions"** section

### Step 2: Ask Questions

Type your question and press **Enter** or click the send button.

**Example Questions:**

#### About Performance
- "What should I focus on first?"
- "Why did Revenue increase this month?"
- "What's causing the expenses spike?"

#### About Trends
- "Explain the Cash Flow trend"
- "Why are Conversions trending down?"
- "Is this growth sustainable?"

#### For Advice
- "How can I improve Leads Generated?"
- "What actions should I take to reduce expenses?"
- "Should I increase ad spend?"

#### For Clarification
- "What does the anomaly in Week 3 mean?"
- "Break down the ROI calculation"
- "Compare to last quarter"

### Step 3: Have a Conversation

The AI remembers your conversation context:
- You: "Why is Revenue up?"
- AI: "Revenue increased 15% due to..."
- You: "What should I do to maintain this?"
- AI: "Based on the trend, I recommend..."

### Step 4: Get Actionable Insights

Ask specific questions to get actionable advice:
- ✅ "How can I increase conversions by 20%?"
- ✅ "What's the best way to reduce customer acquisition cost?"
- ❌ "Tell me about marketing" (too vague)

---

## Complete Workflow Example

### Finance Report Workflow

**1. Setup (One-time)**
```
├─ Create KPIs: Revenue, Expenses, Cash Flow, Overdue Invoices
├─ Set October Goals: Revenue $1.2M, Expenses $450K, etc.
└─ Configure OpenAI API key in Settings
```

**2. Upload September Report**
```
├─ Upload: finance_report_september_2024.csv
├─ View raw data table
└─ Generate analysis for September
```

**3. Upload October Report**
```
├─ Upload: finance_report_october_2024.csv
├─ Generate analysis for October
├─ AI automatically compares to September!
└─ Review recommendations
```

**4. Deep Dive with Chat**
```
You: "Why did expenses increase 40% in October?"
AI: "Expenses rose from $400K to $560K. The increase was primarily..."

You: "How can I reduce expenses?"
AI: "Based on your data, I recommend: 1) Review vendor contracts..."

You: "What's the priority?"
AI: "Focus on the 20% variance in Week 3 first..."
```

**5. Review History**
```
├─ Go to Reports History
├─ See both September and October reports
├─ Click September to compare again
└─ Generate quarterly analysis
```

### Marketing Report Workflow

**1. Setup**
```
├─ Create KPIs: Leads, Ad Spend, CTR, Conversions, etc.
└─ Set Q4 Goals: 6,000 leads, $90K ad spend, 1,000 conversions
```

**2. Upload Monthly Reports**
```
├─ Upload: marketing_report_october_2024.csv
├─ Upload: marketing_report_november_2024.csv
└─ Upload: marketing_report_december_2024.csv
```

**3. Analyze Quarterly Performance**
```
├─ Select any report
├─ Choose "Quarterly" period
├─ Generate analysis
└─ See aggregated Q4 performance vs goals
```

**4. Optimize with AI**
```
You: "Which channel has the best ROI?"
AI: "Based on your data, social media has 4.2x ROI..."

You: "Should I increase budget there?"
AI: "Yes, consider reallocating 30% from email campaigns..."
```

---

## Troubleshooting

### Backend Issues

**Problem: 404 Not Found errors**
```bash
# Solution: Rebuild Docker container
docker-compose down
docker-compose up --build -d
docker-compose exec app alembic upgrade head
```

**Problem: Database connection errors**
```bash
# Check if PostgreSQL is running
docker-compose ps

# Restart database
docker-compose restart db

# Check logs
docker-compose logs db
```

**Problem: Migration errors**
```bash
# Reset and rerun migrations
docker-compose exec app alembic downgrade base
docker-compose exec app alembic upgrade head
```

### Frontend Issues

**Problem: 401 Unauthorized errors**
```
Solution:
1. Go to Settings tab
2. Ensure API key matches backend .env file
3. Default is "devkey"
4. Save and refresh
```

**Problem: Chat returns "Not Found"**
```bash
# Backend needs to be rebuilt
docker-compose down
docker-compose up --build -d
```

**Problem: Reports History is empty**
```
Solution:
1. Upload at least one report first
2. Click "Refresh List" button
3. Check browser console for errors (F12)
```

**Problem: Raw data table not showing**
```
Solution:
1. Ensure you pulled latest code
2. Restart frontend: npm run dev
3. Upload a new report
4. Click "Report Data" to expand
```

### OpenAI Issues

**Problem: "Need OpenAI API key" messages**
```
Solution:
1. Get API key from https://platform.openai.com/api-keys
2. Add to .env file: OPENAI_API_KEY=sk-...
3. Restart Docker: docker-compose restart app
4. System will work with fallback if no key
```

**Problem: Chat is slow or timing out**
```
Solution:
1. Check OpenAI API credits: https://platform.openai.com/usage
2. Verify API key is correct
3. System will use fallback if OpenAI fails
```

### Data Issues

**Problem: KPIs not showing in analysis**
```
Solution:
1. Ensure goals are set for the period
2. Goals period must match analysis period
3. Check date ranges overlap
```

**Problem: File upload fails**
```
Solution:
1. Ensure file has Date column
2. Check file format (CSV, Excel, PDF)
3. Ensure numeric values in KPI columns
4. Remove special characters from headers
```

---

## Tips & Best Practices

### For Best Results

**1. Data Quality**
- Use consistent date formats (YYYY-MM-DD)
- Ensure numeric values are clean (no commas or currency symbols in CSV)
- Include all dates in the period (no gaps)

**2. Goal Setting**
- Set realistic targets based on historical data
- Update goals regularly (monthly/quarterly)
- Align goals with business objectives

**3. Report Organization**
- Name files descriptively: `finance_october_2024.csv`
- Upload reports consistently (same day each period)
- Keep backup copies of original files

**4. Using AI Chat**
- Ask specific questions
- Provide context when needed
- Follow up for clarification
- Use conversation history for context

**5. Analysis Workflow**
- Review raw data first
- Check AI summary
- Read all recommendations
- Use chat for deep dives
- Compare with previous periods

### Time-Saving Tips

**1. Template Reports**
- Use same CSV template each time
- Just update the data rows
- Keep column headers identical

**2. Batch Analysis**
- Upload multiple reports
- Use Reports History to analyze all
- Compare side-by-side

**3. Recurring Questions**
- Keep a list of useful questions
- Ask same questions each period
- Track answers over time

---

## Next Steps

### For Production Use

1. **Security**
   - Change API_KEY to strong random value
   - Use HTTPS for all connections
   - Implement user authentication

2. **Backup**
   - Regular database backups
   - Export important analyses
   - Keep original report files

3. **Scaling**
   - Consider managed PostgreSQL (AWS RDS, etc.)
   - Deploy to cloud (AWS, GCP, Azure)
   - Set up monitoring and alerts

4. **Team Collaboration**
   - Share Reports History
   - Document goal-setting process
   - Create report templates
   - Schedule regular reviews

### Future Enhancements (Coming Soon)

- ✅ Real-time dashboards
- ✅ Automated weekly/monthly reports
- ✅ Email/Slack delivery
- ✅ Zoho API integration
- ✅ Multi-user support
- ✅ Custom visualizations
- ✅ Export to PDF/PowerPoint

---

## Support

**Documentation:**
- README.md - Full project documentation
- QUICKSTART.md - 5-minute setup guide
- API_DOCUMENTATION.md - API reference
- REQUIREMENTS.md - Technical requirements

**Online Resources:**
- FastAPI Docs: http://localhost:8000/docs
- OpenAI Platform: https://platform.openai.com
- Docker Docs: https://docs.docker.com

**Need Help?**
Contact the development team or check the GitHub repository for issues and updates.

---

**Version:** 1.0.0
**Last Updated:** October 26, 2024
**System Status:** ✅ Production Ready
