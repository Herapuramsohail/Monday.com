from fastapi import FastAPI, Query, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from app.config import settings
from app.models.schemas import (
    FilterParams, ChatRequest, SettingsVerifyRequest, SettingsVerifyResponse
)
from app.services.analytics_service import analytics_service
from app.services.monday_service import monday_service
from app.services.ai_service import ai_service
from app.services.summary_service import summary_service
from app.services.cleaner_service import cleaner_service

app = FastAPI(
    title=settings.APP_NAME,
    description="Full-stack AI Business Intelligence API for Monday.com",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": "1.0.0"
    }

@app.get("/dashboard")
def get_dashboard(
    apiToken: Optional[str] = "",
    dealBoardId: Optional[str] = "",
    workBoardId: Optional[str] = "",
    startDate: Optional[str] = None,
    endDate: Optional[str] = None,
    sector: Optional[str] = None,
    dealStage: Optional[str] = None,
    salesperson: Optional[str] = None,
    workOrderStatus: Optional[str] = None,
    customer: Optional[str] = None,
    region: Optional[str] = None
):
    filters = FilterParams(
        startDate=startDate,
        endDate=endDate,
        sector=sector,
        dealStage=dealStage,
        salesperson=salesperson,
        workOrderStatus=workOrderStatus,
        customer=customer,
        region=region
    )
    return analytics_service.get_dashboard_data(apiToken, dealBoardId, workBoardId, filters)

@app.get("/deals")
def get_deals(
    apiToken: Optional[str] = "",
    dealBoardId: Optional[str] = "",
    startDate: Optional[str] = None,
    endDate: Optional[str] = None,
    sector: Optional[str] = None,
    dealStage: Optional[str] = None,
    salesperson: Optional[str] = None
):
    all_deals = monday_service.fetch_deals_data(apiToken, dealBoardId)
    filters = FilterParams(startDate=startDate, endDate=endDate, sector=sector, dealStage=dealStage, salesperson=salesperson)
    filtered_deals = analytics_service.filter_deals(all_deals, filters)
    return {"deals": filtered_deals, "count": len(filtered_deals)}

@app.get("/workorders")
def get_work_orders(
    apiToken: Optional[str] = "",
    workBoardId: Optional[str] = "",
    startDate: Optional[str] = None,
    endDate: Optional[str] = None,
    sector: Optional[str] = None,
    workOrderStatus: Optional[str] = None,
    customer: Optional[str] = None
):
    all_work = monday_service.fetch_work_orders_data(apiToken, workBoardId)
    filters = FilterParams(startDate=startDate, endDate=endDate, sector=sector, workOrderStatus=workOrderStatus, customer=customer)
    filtered_work = analytics_service.filter_work_orders(all_work, filters)
    return {"workOrders": filtered_work, "count": len(filtered_work)}

@app.post("/chat")
def chat_assistant(req: ChatRequest):
    return ai_service.process_query(
        message=req.message,
        filters=req.filters
    )

@app.post("/summary")
def get_summary(
    apiToken: Optional[str] = "",
    dealBoardId: Optional[str] = "",
    workBoardId: Optional[str] = ""
):
    return summary_service.generate_summary(apiToken, dealBoardId, workBoardId)

@app.post("/forecast")
def get_forecast(
    apiToken: Optional[str] = "",
    dealBoardId: Optional[str] = "",
    workBoardId: Optional[str] = ""
):
    dash = analytics_service.get_dashboard_data(apiToken, dealBoardId, workBoardId)
    return {"forecast": dash.charts.revenueForecast, "expectedRevenue": dash.kpis.expectedRevenue}

@app.get("/data-quality")
def get_data_quality(
    apiToken: Optional[str] = "",
    dealBoardId: Optional[str] = "",
    workBoardId: Optional[str] = ""
):
    deals = monday_service.fetch_deals_data(apiToken, dealBoardId)
    work = monday_service.fetch_work_orders_data(apiToken, workBoardId)

    score = cleaner_service.get_confidence_score(len(deals), len(work))
    missing_vals = cleaner_service._missing_count
    dups = cleaner_service._duplicate_count
    date_fixes = cleaner_service._date_fix_count
    sectors_fixed = cleaner_service._sector_fix_count
    incomplete_wo = cleaner_service._incomplete_work_orders

    return {
        "confidenceScore": score,
        "missingValuesCount": missing_vals,
        "duplicateRecordsCount": dups,
        "invalidDatesFixed": date_fixes,
        "emptySectorsHandled": sectors_fixed,
        "incompleteWorkOrders": incomplete_wo,
        "totalCleanedDeals": len(deals),
        "totalCleanedWorkOrders": len(work),
        "logs": cleaner_service.logs
    }

@app.get("/search")
def global_search(query: str):
    return analytics_service.global_search(query)

@app.post("/settings/verify")
def verify_settings(req: SettingsVerifyRequest):
    success, msg, details = monday_service.verify_connection(
        req.mondayApiToken, req.dealBoardId, req.workBoardId
    )
    return SettingsVerifyResponse(
        success=success,
        message=msg,
        dealBoardName=details.get("dealBoardName"),
        workBoardName=details.get("workBoardName"),
        dealItemsCount=details.get("dealItemsCount", 0),
        workItemsCount=details.get("workItemsCount", 0)
    )
