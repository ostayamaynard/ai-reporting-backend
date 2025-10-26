# Zoho Form Template for Project Requests

This document provides the template and configuration for creating a Zoho Form that allows users to request custom reports or new projects from the AI Reporting system.

## Form Purpose

This form enables stakeholders to:
- Request custom reports
- Submit new project ideas
- Request modifications to existing reports
- Provide feedback on AI agents

## Zoho Form Configuration

### Form Name
**AI Reporting - Project & Report Request Form**

### Form Fields

#### Section 1: Requester Information

1. **Name** (Single Line)
   - Required: Yes
   - Placeholder: "Your Full Name"

2. **Email** (Email)
   - Required: Yes
   - Validation: Email format
   - Placeholder: "your.email@company.com"

3. **Department** (Dropdown)
   - Required: Yes
   - Options:
     - Finance
     - Marketing
     - Sales
     - Operations
     - Executive
     - IT
     - Other

4. **Role/Title** (Single Line)
   - Required: No
   - Placeholder: "Your Job Title"

#### Section 2: Request Type

5. **Request Type** (Radio Button)
   - Required: Yes
   - Options:
     - Custom Report Request
     - New Project/Agent Request
     - Modify Existing Report
     - Feature Enhancement
     - Bug Report
     - General Feedback

#### Section 3: Report Details (Conditional - if "Custom Report Request")

6. **Report Category** (Dropdown)
   - Required: Yes
   - Options:
     - Finance
     - Marketing
     - Sales
     - Combined (Multi-department)
     - Other

7. **Report Frequency** (Radio Button)
   - Required: Yes
   - Options:
     - One-time
     - Weekly
     - Bi-weekly
     - Monthly
     - Quarterly
     - Custom Schedule

8. **Custom Schedule Details** (Single Line)
   - Required: Only if "Custom Schedule" selected
   - Placeholder: "Describe your preferred schedule"

9. **Data Sources Required** (Multi-select Checkbox)
   - Required: Yes
   - Options:
     - Zoho Books
     - Zoho CRM
     - Zoho Marketing Hub
     - Zoho Analytics
     - Other (please specify)

10. **Specific Metrics/KPIs Needed** (Multi-line Text)
    - Required: Yes
    - Placeholder: "List the specific metrics, KPIs, or data points you need in this report"
    - Rows: 4

11. **Date Range** (Dropdown)
    - Required: Yes
    - Options:
      - Last 7 days
      - Last 30 days
      - Last quarter
      - Last year
      - Custom (specify in description)
      - Year-to-date
      - Month-to-date

#### Section 4: Project Details (Conditional - if "New Project/Agent Request")

12. **Project Name** (Single Line)
    - Required: Yes
    - Placeholder: "Brief project name"

13. **Project Objective** (Multi-line Text)
    - Required: Yes
    - Placeholder: "What business problem does this solve?"
    - Rows: 4

14. **Expected Outcomes** (Multi-line Text)
    - Required: Yes
    - Placeholder: "What are the expected deliverables?"
    - Rows: 4

15. **Data Sources Needed** (Multi-line Text)
    - Required: Yes
    - Placeholder: "List all data sources and systems needed"
    - Rows: 3

16. **Stakeholders** (Multi-line Text)
    - Required: No
    - Placeholder: "Who will use this? (teams, roles, individuals)"
    - Rows: 2

#### Section 5: Modification Request (Conditional - if "Modify Existing Report")

17. **Existing Report Name/ID** (Single Line)
    - Required: Yes
    - Placeholder: "Which report needs modification?"

18. **What needs to change?** (Multi-line Text)
    - Required: Yes
    - Placeholder: "Describe the changes needed"
    - Rows: 4

19. **Reason for Change** (Multi-line Text)
    - Required: No
    - Placeholder: "Why is this change needed?"
    - Rows: 3

#### Section 6: Additional Details (All Request Types)

20. **Detailed Description** (Multi-line Text)
    - Required: Yes
    - Placeholder: "Provide a detailed description of your request"
    - Rows: 6

21. **Business Impact** (Radio Button)
    - Required: Yes
    - Options:
      - Critical - Blocking work
      - High - Significant impact
      - Medium - Helpful improvement
      - Low - Nice to have

22. **Timeline/Urgency** (Dropdown)
    - Required: Yes
    - Options:
      - ASAP (within 1 week)
      - 2-4 weeks
      - 1-3 months
      - No rush
      - Specific deadline (specify in notes)

23. **Specific Deadline** (Date)
    - Required: Only if "Specific deadline" selected
    - Format: MM/DD/YYYY

24. **Preferred Delivery Method** (Multi-select Checkbox)
    - Required: Yes
    - Options:
      - Email
      - Slack
      - API Integration
      - Dashboard
      - Other (specify)

25. **Delivery Recipients** (Multi-line Text)
    - Required: No
    - Placeholder: "Email addresses or Slack channels for delivery"
    - Rows: 2

26. **Budget/Resources** (Single Line)
    - Required: No
    - Placeholder: "Any budget constraints or resource availability?"

27. **Additional Notes** (Multi-line Text)
    - Required: No
    - Placeholder: "Any other information we should know?"
    - Rows: 4

28. **Attachments** (File Upload)
    - Required: No
    - Allowed types: PDF, XLSX, CSV, PNG, JPG
    - Max size: 10MB
    - Help text: "Upload any supporting documents, examples, or mockups"

#### Section 7: Approval (Optional for enterprise setup)

29. **Manager Approval Required?** (Radio Button)
    - Required: Yes
    - Options:
      - Yes
      - No

30. **Manager Email** (Email)
    - Required: Only if "Yes" for approval
    - Placeholder: "manager@company.com"

### Form Settings

**General Settings**:
- Allow multiple submissions: Yes
- Save and resume later: Yes
- Show progress bar: Yes
- Submission message: "Thank you! Your request has been submitted. You'll receive a confirmation email shortly."

**Notifications**:
1. **To Requester**:
   - Send confirmation email
   - Include submission details
   - Estimated response time

2. **To Admin Team**:
   - Email to: ai-reporting-admin@company.com
   - Subject: "New AI Reporting Request - [Request Type]"
   - Include all form data

3. **To Manager** (if approval required):
   - Email with approval link
   - Subject: "Approval Required - AI Reporting Request"

**Conditional Logic**:
- Show "Report Details" section only if Request Type = "Custom Report Request"
- Show "Project Details" section only if Request Type = "New Project/Agent Request"
- Show "Modification Request" section only if Request Type = "Modify Existing Report"
- Show "Manager Email" only if "Manager Approval Required" = "Yes"

### Integration with AI Reporting Backend

Create a Zoho Flow or webhook to:

1. **Capture Form Submission**
   ```javascript
   // Webhook URL
   POST https://your-domain.com/api/v1/forms/project-request
   ```

2. **Payload Structure**
   ```json
   {
     "requester": {
       "name": "John Doe",
       "email": "john@company.com",
       "department": "Finance",
       "role": "CFO"
     },
     "request_type": "Custom Report Request",
     "details": {
       "report_category": "Finance",
       "frequency": "Weekly",
       "metrics": ["Revenue", "Cash Flow", "AR Aging"],
       "date_range": "Last 30 days"
     },
     "priority": "High",
     "timeline": "2-4 weeks",
     "description": "Need weekly cash flow monitoring...",
     "delivery": {
       "methods": ["Email", "Slack"],
       "recipients": ["finance-team@company.com"]
     }
   }
   ```

3. **Create Backend Endpoint**

Add to `app/routers/forms.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/forms", tags=["Forms"])

class ProjectRequest(BaseModel):
    requester_name: str
    requester_email: str
    department: str
    request_type: str
    description: str
    priority: str
    timeline: str
    # ... other fields

@router.post("/project-request")
async def handle_project_request(request: ProjectRequest):
    # Process the request
    # Store in database
    # Send notifications
    # Create tracking ticket
    return {"status": "success", "request_id": "REQ-12345"}
```

## Using the Form

### Access URL
Share the form URL with stakeholders:
```
https://forms.zohopublic.com/yourorg/form/AIReportingProjectRequest
```

### Embedding in Website
```html
<iframe
  src="https://forms.zohopublic.com/yourorg/form/AIReportingProjectRequest"
  width="100%"
  height="800px"
  frameborder="0">
</iframe>
```

### QR Code
Generate QR code for the form for easy mobile access.

## Form Administration

### Viewing Submissions
1. Log in to Zoho Forms
2. Navigate to "Responses"
3. Filter by date, department, request type

### Export Submissions
- Export to Excel for tracking
- Generate reports on request types
- Analyze trends

### Follow-up Workflow

1. **Automatic Acknowledgment**
   - Requester receives confirmation email
   - Request ID generated
   - Expected timeline communicated

2. **Admin Review**
   - Admin team receives notification
   - Reviews request for feasibility
   - Assigns to appropriate team member

3. **Approval Process** (if required)
   - Manager receives approval request
   - Can approve/reject with comments
   - Requester notified of decision

4. **Implementation**
   - Request added to project backlog
   - Development team implements
   - Testing and QA

5. **Delivery**
   - Requester notified of completion
   - Training provided if needed
   - Feedback collected

## Reporting on Form Submissions

Track key metrics:
- Number of requests by type
- Average time to completion
- Most requested features
- Departments with most requests
- Approval rate

## Best Practices

1. **Clear Communication**
   - Provide examples in form fields
   - Set expectations on timeline
   - Be transparent about feasibility

2. **Regular Updates**
   - Send status updates to requesters
   - Maintain request tracking system
   - Close loop with completion notification

3. **Continuous Improvement**
   - Regularly review form effectiveness
   - Update based on common questions
   - Streamline approval process

## Sample Completed Form

**Example Finance Report Request**:
```
Name: Jane Smith
Email: jane.smith@company.com
Department: Finance
Request Type: Custom Report Request
Report Category: Finance
Frequency: Weekly
Metrics Needed:
  - Cash flow by week
  - AR aging summary
  - Top 10 overdue invoices
  - Collection rate
Priority: High
Timeline: 2-4 weeks
Delivery: Email to finance-team@company.com, Slack #finance channel
Description: Need automated weekly cash flow monitoring to replace manual Excel tracking
```

## Support

For questions about the form:
- Form Admin: forms-admin@company.com
- Technical Support: it-support@company.com
- AI Reporting Team: ai-reporting@company.com
