# API Documentation - AI Reporting System

Complete API reference for the AI Reporting System backend.

## Base URL

```
http://localhost:8000
```

## Authentication

All endpoints (except `/health`) require API key authentication via header:

```
X-API-Key: dev-key-12345
```

**Production Note:** Change the API key in `.env` for production environments.

## Response Format

### Success Response
```json
{
  "data": { ... },
  "status": "success"
}
```

### Error Response
```json
{
  "detail": "Error message here"
}
```

## Endpoints

### Health Check

Check if the API is running.

**Endpoint:** `GET /health`

**Authentication:** Not required

**Response:**
```json
{
  "status": "ok"
}
```

**Example:**
```bash
curl http://localhost:8000/health
```

---

## KPI Management

### Create KPI

Create a new Key Performance Indicator.

**Endpoint:** `POST /kpis`

**Headers:**
```
X-API-Key: dev-key-12345
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "Revenue",
  "unit": "USD",
  "aggregation": "sum"
}
```

**Fields:**
- `name` (string, required): Unique KPI name
- `unit` (string, optional): Unit of measurement (e.g., "USD", "count", "%")
- `aggregation` (string, required): Aggregation method - `"sum"` or `"avg"`

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "Revenue",
  "unit": "USD",
  "aggregation": "sum"
}
```

**Example:**
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

### List KPIs

Get all KPIs in the system.

**Endpoint:** `GET /kpis`

**Headers:**
```
X-API-Key: dev-key-12345
```

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "name": "Revenue",
    "unit": "USD",
    "aggregation": "sum"
  },
  {
    "id": 2,
    "name": "Expenses",
    "unit": "USD",
    "aggregation": "sum"
  }
]
```

**Example:**
```bash
curl http://localhost:8000/kpis \
  -H "X-API-Key: dev-key-12345"
```

---

## Goal Management

### Create Goals

Set targets for KPIs for a specific period.

**Endpoint:** `POST /goals`

**Headers:**
```
X-API-Key: dev-key-12345
Content-Type: application/json
```

**Request Body:**
```json
{
  "period_type": "monthly",
  "period_start": "2024-10-01",
  "period_end": "2024-10-31",
  "items": [
    {
      "kpi": "Revenue",
      "target_value": 1500000,
      "unit": "USD",
      "aggregation": "sum"
    },
    {
      "kpi": "Expenses",
      "target_value": 600000,
      "unit": "USD",
      "aggregation": "sum"
    }
  ]
}
```

**Fields:**
- `period_type` (string, required): `"monthly"` or `"quarterly"`
- `period_start` (date, required): Start date in YYYY-MM-DD format
- `period_end` (date, required): End date in YYYY-MM-DD format
- `items` (array, required): List of KPI targets
  - `kpi` (string, required): KPI name (will be created if doesn't exist)
  - `target_value` (number, required): Target value for this KPI
  - `unit` (string, optional): Unit of measurement
  - `aggregation` (string, optional): Aggregation method

**Response:** `200 OK`
```json
{
  "message": "Goals created",
  "count": 2
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/goals \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

---

## Report Management

### Upload Report

Upload a report file for processing.

**Endpoint:** `POST /reports/upload`

**Headers:**
```
X-API-Key: dev-key-12345
Content-Type: multipart/form-data
```

**Request Body:**
- `file` (file, required): Report file

**Supported Formats:**
- CSV (`.csv`)
- TSV (`.tsv`)
- Excel (`.xlsx`, `.xls`)
- PDF (`.pdf`)

**CSV/Excel Format Requirements:**
- Must have a header row
- First column should be "Date" in YYYY-MM-DD format
- Subsequent columns are KPI names with numeric values

**Example CSV:**
```csv
Date,Revenue,Expenses,Cash Flow
2024-10-01,50000,15000,35000
2024-10-02,52000,16000,36000
```

**Response:** `200 OK`
```json
{
  "report_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "uploaded"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/reports/upload \
  -H "X-API-Key: dev-key-12345" \
  -F "file=@path/to/report.csv"
```

**Notes:**
- KPIs are automatically created if they don't exist
- All values are aggregated by date
- PDF files are parsed for tabular data

---

## Analysis

### Generate AI Analysis

Analyze a report against goals and previous reports.

**Endpoint:** `POST /analyze`

**Headers:**
```
X-API-Key: dev-key-12345
Content-Type: application/json
```

**Request Body:**
```json
{
  "report_id": "550e8400-e29b-41d4-a716-446655440000",
  "goal_period": "monthly"
}
```

**Fields:**
- `report_id` (string, required): Report ID from upload response
- `goal_period` (string, required): `"monthly"` or `"quarterly"`

**Response:** `200 OK`
```json
{
  "summary_md": "# Analysis Summary\n\n**Verdict: On track**\n\n- Revenue exceeded target by $80,000 (5.3%)\n- Expenses below target by $20,000 (3.3%)\n- Cash Flow trending up vs last month\n- No significant anomalies detected",
  "kpi_table": [
    {
      "kpi": "Revenue",
      "target": 1500000,
      "actual": 1580000,
      "variance": 80000,
      "status": "above"
    },
    {
      "kpi": "Expenses",
      "target": 600000,
      "actual": 580000,
      "variance": -20000,
      "status": "below"
    }
  ],
  "anomalies": [
    {
      "kpi": "Overdue Invoices",
      "note": "Variance 15000.00 exceeds 20% of target"
    }
  ],
  "trend": {
    "Revenue": "up",
    "Expenses": "down",
    "Cash Flow": "up",
    "Overdue Invoices": "up"
  }
}
```

**Response Fields:**
- `summary_md` (string): Markdown-formatted AI-generated summary
- `kpi_table` (array): Comparison of targets vs actuals
  - `kpi`: KPI name
  - `target`: Target value from goals
  - `actual`: Actual value from report
  - `variance`: Difference (actual - target)
  - `status`: `"above"` or `"below"` target
- `anomalies` (array): KPIs with >20% variance from target
  - `kpi`: KPI name
  - `note`: Description of anomaly
- `trend` (object): Trend direction for each KPI
  - Values: `"up"`, `"down"`, or `"flat"`

**Example:**
```bash
curl -X POST http://localhost:8000/analyze \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "report_id": "550e8400-e29b-41d4-a716-446655440000",
    "goal_period": "monthly"
  }'
```

**Analysis Features:**
1. **Goal Comparison**: Compares actual values against set targets
2. **Previous Report Comparison**: Automatically compares with the most recent previous report
3. **Anomaly Detection**: Identifies variances >20% from target
4. **Trend Analysis**: Determines if KPIs are trending up, down, or flat
5. **AI Summary**: Generates executive-level insights (requires OpenAI API key)

---

## Error Codes

| HTTP Code | Description |
|-----------|-------------|
| `200` | Success |
| `400` | Bad Request - Invalid input data |
| `401` | Unauthorized - Invalid or missing API key |
| `404` | Not Found - Resource doesn't exist |
| `422` | Unprocessable Entity - Validation error |
| `500` | Internal Server Error |

## Error Examples

### Invalid File Format
```json
{
  "detail": "Unsupported file type"
}
```

### Missing API Key
```json
{
  "detail": "Not authenticated"
}
```

### Report Not Found
```json
{
  "detail": "Report not found"
}
```

### Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Data Models

### KPI Model
```json
{
  "id": 1,
  "name": "Revenue",
  "unit": "USD",
  "aggregation": "sum"
}
```

### Goal Model
```json
{
  "id": 1,
  "kpi_id": 1,
  "period_type": "monthly",
  "period_start": "2024-10-01",
  "period_end": "2024-10-31",
  "target_value": 1500000
}
```

### Report Model
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "file_uri": "/app/data/uploads/550e8400-e29b-41d4-a716-446655440000.csv",
  "source": "upload",
  "period_start": "2024-10-01",
  "period_end": "2024-10-31",
  "status": "parsed",
  "created_at": "2024-10-26T10:30:00Z"
}
```

### Report Metric Model
```json
{
  "id": 1,
  "report_id": "550e8400-e29b-41d4-a716-446655440000",
  "kpi_id": 1,
  "value": 50000,
  "date": "2024-10-01"
}
```

### Analysis Model
```json
{
  "id": 1,
  "report_id": "550e8400-e29b-41d4-a716-446655440000",
  "goal_period": "monthly",
  "summary_md": "# Analysis...",
  "comparisons_json": [...],
  "created_at": "2024-10-26T10:35:00Z"
}
```

## Rate Limits

Currently no rate limits are enforced in development mode.

**Production Recommendations:**
- Implement rate limiting (e.g., 100 requests/minute per API key)
- Use Redis for distributed rate limiting
- Monitor usage patterns

## OpenAI Integration

The `/analyze` endpoint can use OpenAI for enhanced analysis.

**Configuration:**
```bash
# In .env file
OPENAI_API_KEY=sk-your-key-here
```

**Behavior:**
- **With OpenAI Key**: Uses GPT-4o-mini for rich, contextual analysis
- **Without OpenAI Key**: Uses fallback logic for structured summaries

**OpenAI Usage:**
- Model: `gpt-4o-mini`
- Temperature: 0.2 (more deterministic)
- Max tokens: ~500 per analysis
- Cost: ~$0.001 per analysis

## Interactive API Documentation

FastAPI provides interactive API documentation:

**Swagger UI:**
```
http://localhost:8000/docs
```

**ReDoc:**
```
http://localhost:8000/redoc
```

Features:
- Try out API endpoints directly
- View request/response schemas
- Download OpenAPI specification

## Webhooks (Future)

Currently not implemented. Future versions may support:
- Report upload notifications
- Analysis completion webhooks
- Goal achievement alerts

## Versioning

Current API version: `v1` (implicit)

Future versions will use URL versioning:
```
http://localhost:8000/api/v2/kpis
```

## SDK / Client Libraries

Currently, no official SDKs. Use standard HTTP clients:

**Python:**
```python
import requests

headers = {"X-API-Key": "dev-key-12345"}
response = requests.get("http://localhost:8000/kpis", headers=headers)
kpis = response.json()
```

**JavaScript:**
```javascript
const headers = { "X-API-Key": "dev-key-12345" };
const response = await fetch("http://localhost:8000/kpis", { headers });
const kpis = await response.json();
```

**cURL:**
```bash
curl -H "X-API-Key: dev-key-12345" http://localhost:8000/kpis
```

## Support

For API support, contact the development team.
