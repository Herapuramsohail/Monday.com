try:
    from pydantic import BaseModel, Field
    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False

if HAS_PYDANTIC:
    class FilterParams(BaseModel):
        startDate: str = None
        endDate: str = None
        sector: str = None
        dealStage: str = None
        salesperson: str = None
        workOrderStatus: str = None
        customer: str = None
        region: str = None

    class KPICards(BaseModel):
        totalDeals: int
        openDeals: int
        closedDeals: int
        totalPipelineValue: float
        expectedRevenue: float
        activeWorkOrders: int
        completedWorkOrders: int
        delayedWorkOrders: int
        averageDealSize: float
        conversionRate: float

    class ChartDataPoint(BaseModel):
        name: str
        value: float
        count: int = 0
        secondaryValue: float = 0.0

    class ChartDataset(BaseModel):
        pipelineByStage: list[ChartDataPoint]
        revenueBySector: list[ChartDataPoint]
        revenueBySalesperson: list[ChartDataPoint]
        dealsByMonth: list[ChartDataPoint]
        workOrdersByStatus: list[ChartDataPoint]
        projectCompletionTrend: list[ChartDataPoint]
        sectorDistribution: list[ChartDataPoint]
        revenueForecast: list[ChartDataPoint]

    class DashboardResponse(BaseModel):
        kpis: KPICards
        charts: ChartDataset
        sectors: list[str]
        salespersons: list[str]
        dealStages: list[str]
        workOrderStatuses: list[str]
        customers: list[str]
        dataConfidenceScore: float
        totalRecords: int

    class ChatRequest(BaseModel):
        message: str
        filters: FilterParams = None

    class ChatResponse(BaseModel):
        reply: str
        toolCalls: list[dict] = []

    class ExecutiveSummaryResponse(BaseModel):
        title: str = "Executive Business Summary"
        generatedAt: str
        totalPipelineFormatted: str
        activeDealsCount: int
        expectedRevenueQuarterFormatted: str
        bestPerformingSector: str
        worstPerformingSector: str
        delayedProjectsCount: int
        delayedProjectNames: list[str]
        majorBusinessRisks: list[str]
        recommendedActions: list[str]
        summaryTextMarkdown: str

    class DataQualityLog(BaseModel):
        timestamp: str
        field: str
        operation: str
        affectedCount: int
        details: str

    class SettingsVerifyRequest(BaseModel):
        mondayApiToken: str
        dealBoardId: str
        workBoardId: str

    class SettingsVerifyResponse(BaseModel):
        success: bool
        message: str
        dealBoardName: str = None
        workBoardName: str = None
        dealItemsCount: int = 0
        workItemsCount: int = 0

else:
    # Pure Python Fallback implementation
    class BaseDictModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
        def model_dump(self):
            res = {}
            for k, v in self.__dict__.items():
                if hasattr(v, 'model_dump'):
                    res[k] = v.model_dump()
                elif isinstance(v, list):
                    res[k] = [item.model_dump() if hasattr(item, 'model_dump') else item for item in v]
                else:
                    res[k] = v
            return res

    class FilterParams(BaseDictModel):
        def __init__(self, startDate=None, endDate=None, sector=None, dealStage=None, salesperson=None, workOrderStatus=None, customer=None, region=None):
            super().__init__(startDate=startDate, endDate=endDate, sector=sector, dealStage=dealStage, salesperson=salesperson, workOrderStatus=workOrderStatus, customer=customer, region=region)

    class KPICards(BaseDictModel): pass
    class ChartDataPoint(BaseDictModel): pass
    class ChartDataset(BaseDictModel): pass
    class DashboardResponse(BaseDictModel): pass
    class ChatRequest(BaseDictModel): pass
    class ChatResponse(BaseDictModel): pass
    class ExecutiveSummaryResponse(BaseDictModel): pass
    class DataQualityLog(BaseDictModel): pass
    class SettingsVerifyRequest(BaseDictModel): pass
    class SettingsVerifyResponse(BaseDictModel): pass
