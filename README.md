# Monday.com AI Business Intelligence Agent

A full-stack, AI-powered Business Intelligence web application that connects dynamically to Monday.com boards (Deal Funnel & Work Order Tracker) using Monday's GraphQL API. 

## Features

1. **Executive BI Dashboard**: View key business indicators (Total Pipeline, Active Deals, Expected Revenue, Delayed Projects, average deal size, conversion rate) and interactive Recharts.
2. **Tabular Boards**: Granular tables for Deal Funnel and Work Order Tracker with live filters, searches, and status badges.
3. **AI Chat Assistant**: Natural language querying with custom tool-calling sandboxes to perform math calculations, lookup deals/work orders, analyze sectors, and forecast revenue.
4. **Data Cleaning Layer**: Automated Pandas/NumPy-like pipelines to handle missing values, duplicates, parse dates, format currency, and log cleaning audits.
5. **Executive Summary Generator**: Automate leadership reports formatted for corporate presentation with client-side PDF export.
6. **Data Quality Auditor**: Review dataset confidence scores and step-by-step cleaning logs.
7. **Credentials & Settings**: Verify and test personal Monday.com GraphQL API tokens and Board IDs.

---

## Workspace Setup & Running Locally

The project is structured inside: `C:\Users\Muskan\.gemini\antigravity\scratch\monday-bi-agent`

### 1. Start the Python Backend Server
Start the backend server using standard python libraries (no dependencies required):
```bash
cd backend
python app/standalone_server.py
```
This runs the local API server on `http://127.0.0.1:8000`.

### 2. Launch the BI Interface
Since Node/npm might not be installed globally on your machine, we have built a **Zero-Install Interactive Dashboard**:
1. Open the file [dashboard.html](file:///C:/Users/Muskan/.gemini/antigravity/scratch/monday-bi-agent/dashboard.html) in any web browser.
2. It will connect to your running Python backend server dynamically!

---

## Production Next.js Codebase
The complete production-ready Next.js & TypeScript codebase is located under the `frontend/` directory.

To run the Next.js app once Node.js is installed:
```bash
cd frontend
npm install
npm run dev
```

---

## Deployment Configuration

### Backend: Render Deployment
1. Create a Web Service on Render.
2. Set Environment Variables:
   - `MONDAY_API_TOKEN`
   - `MONDAY_DEAL_BOARD_ID`
   - `MONDAY_WORK_BOARD_ID`
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Frontend: Vercel Deployment
1. Import the `frontend/` directory into Vercel.
2. Add Environmental Variable:
   - `NEXT_PUBLIC_API_URL` pointing to your deployed Render URL.
3. Deploy!
