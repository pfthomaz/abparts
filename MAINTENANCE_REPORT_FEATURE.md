# Maintenance Execution Report Feature

## Overview
This feature adds AI-powered report generation for maintenance executions, allowing users to download comprehensive reports in DOCX or PDF format with AI-generated insights for each task.

## Features

### 1. Report Generation
- **DOCX Format**: Professional Word document with formatted tables and sections
- **PDF Format**: Print-ready PDF with styled layout
- **AI Insights**: Each checklist item includes AI-generated expert commentary on:
  - Why the task is important
  - Potential issues if not completed properly
  - Best practices and recommendations

### 2. Report Contents
- **Execution Metadata**:
  - Organization name
  - Machine details (name, serial number)
  - Protocol name
  - Performed by (technician)
  - Date and time
  - Machine hours at service
  - Execution status

- **General Notes**: Any overall notes from the execution

- **Checklist Items** (for each task):
  - Task description
  - Category
  - Completion status
  - Completion timestamp
  - Technician notes
  - AI-generated expert insights

### 3. Access Control
- Users can only download reports for executions in their organization
- Super admins can download any report
- Reports are generated on-demand (not pre-generated)

## Usage

### From the UI
1. Navigate to Maintenance Executions
2. Click on any execution to view details
3. Click the "📄 DOCX" or "📑 PDF" button in the top-right corner
4. The report will be generated and downloaded automatically

### API Endpoints

#### Download DOCX Report
```
GET /maintenance-protocols/executions/{execution_id}/report/docx
```

#### Download PDF Report
```
GET /maintenance-protocols/executions/{execution_id}/report/pdf
```

Both endpoints require authentication and return the file as a download.

## Configuration

### OpenAI API Key
The AI insights feature requires an OpenAI API key. Set it in your `.env` file:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

If the API key is not configured, reports will still generate but with a placeholder message for AI insights.

### Model Configuration
The service uses `gpt-3.5-turbo` by default. You can modify this in:
`backend/app/services/maintenance_report_service.py`

## Technical Details

### Backend Components
- **Service**: `backend/app/services/maintenance_report_service.py`
  - `MaintenanceReportService` class handles report generation
  - `generate_docx_report()` - Creates Word documents
  - `generate_pdf_report()` - Creates PDF documents
  - `generate_ai_insights()` - Calls OpenAI API for insights

- **Router**: `backend/app/routers/maintenance_protocols.py`
  - Two new endpoints for DOCX and PDF downloads
  - Includes permission checks and organization validation

### Frontend Components
- **Component**: `frontend/src/components/ExecutionHistory.js`
  - Added download buttons in execution details view
  - Buttons trigger direct download from API

### Dependencies
- `python-docx==1.1.0` - DOCX generation
- `reportlab==4.0.7` - PDF generation
- `openai==1.3.0` - AI insights generation

## File Naming Convention
Reports are automatically named with the following pattern:
```
Maintenance_Report_{Protocol_Name}_{Machine_Name}_{Date}.{ext}
```

Example:
```
Maintenance_Report_Pre-Commission_Audit_Checklist_AutoBoss_X1_20260218.docx
```

## Performance Considerations
- Reports are generated on-demand (not cached)
- AI insights add ~2-5 seconds per checklist item
- For protocols with many items, generation may take 30-60 seconds
- Consider adding a loading indicator for better UX

## Future Enhancements
- [ ] Add report templates for different protocol types
- [ ] Include photos/attachments in reports
- [ ] Add batch report generation for multiple executions
- [ ] Cache AI insights to avoid regenerating
- [ ] Add report scheduling/email delivery
- [ ] Support for custom report branding/logos
- [ ] Multi-language report generation

## Troubleshooting

### Reports not downloading
- Check that the API container has the required packages installed
- Verify OpenAI API key is set (for AI insights)
- Check browser console for errors
- Verify user has permission to access the execution

### AI insights not appearing
- Verify `OPENAI_API_KEY` is set in `.env`
- Check API container logs for OpenAI API errors
- Ensure OpenAI account has sufficient credits

### Dependency conflicts
If you see httpx version conflicts with googletrans:
```bash
# This is expected and won't affect report generation
# The newer httpx version is required for openai package
```

## Testing
To test the feature:
1. Create a maintenance execution with checklist items
2. Add notes to some checklist items
3. Complete the execution
4. View the execution details
5. Click DOCX or PDF download button
6. Verify the report contains all expected data and AI insights
