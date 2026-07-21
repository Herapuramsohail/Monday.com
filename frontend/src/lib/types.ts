export interface FilterParams {
  startDate?: string;
  endDate?: string;
  sector?: string;
  dealStage?: string;
  salesperson?: string;
  workOrderStatus?: string;
  customer?: string;
  region?: string;
}

export interface KPICards {
  totalDeals: number;
  openDeals: number;
  closedDeals: number;
  totalPipelineValue: number;
  expectedRevenue: number;
  activeWorkOrders: number;
  completedWorkOrders: number;
  delayedWorkOrders: number;
  averageDealSize: number;
  conversionRate: number;
}

export interface ChartDataPoint {
  name: string;
  value: number;
  count?: number;
  secondaryValue?: number;
}

export interface ChartDataset {
  pipelineByStage: ChartDataPoint[];
  revenueBySector: ChartDataPoint[];
  revenueBySalesperson: ChartDataPoint[];
  dealsByMonth: ChartDataPoint[];
  workOrdersByStatus: ChartDataPoint[];
  projectCompletionTrend: ChartDataPoint[];
  sectorDistribution: ChartDataPoint[];
  revenueForecast: ChartDataPoint[];
}

export interface DashboardResponse {
  kpis: KPICards;
  charts: ChartDataset;
  sectors: string[];
  salespersons: string[];
  dealStages: string[];
  workOrderStatuses: string[];
  customers: string[];
  dataConfidenceScore: number;
  totalRecords: number;
}

export interface DealItem {
  dealName: string;
  ownerCode: string;
  clientCode: string;
  dealStatus: string;
  closeDateActual?: string;
  closureProbability: string;
  maskedDealValue: number;
  tentativeCloseDate?: string;
  dealStage: string;
  productDeal: string;
  sector: string;
  createdDate?: string;
  cleaningBadges: string[];
}

export interface WorkOrderItem {
  dealName: string;
  customerNameCode: string;
  serialNo: string;
  natureOfWork: string;
  executionStatus: string;
  dataDeliveryDate?: string;
  dateOfPO?: string;
  documentType: string;
  probableStartDate?: string;
  probableEndDate?: string;
  bdPersonnelCode: string;
  sector: string;
  typeOfWork: string;
  amountRupeesExclGST: number;
  amountRupeesInclGST: number;
  billedValueExclGST: number;
  collectedAmountInclGST: number;
  amountToBeBilledExclGST: number;
  amountReceivable: number;
  woStatusBilled: string;
  billingStatus: string;
  isDelayed: boolean;
  cleaningBadges: string[];
}

export interface ChatResponse {
  reply: string;
  toolCalls: any[];
}

export interface ExecutiveSummaryResponse {
  title: string;
  generatedAt: string;
  totalPipelineFormatted: string;
  activeDealsCount: number;
  expectedRevenueQuarterFormatted: string;
  bestPerformingSector: string;
  worstPerformingSector: string;
  delayedProjectsCount: number;
  delayedProjectNames: string[];
  majorBusinessRisks: string[];
  recommendedActions: string[];
  summaryTextMarkdown: string;
}

export interface DataQualityLog {
  timestamp: string;
  field: string;
  operation: string;
  affectedCount: number;
  details: string;
}

export interface DataQualityReportResponse {
  confidenceScore: number;
  missingValuesCount: number;
  duplicateRecordsCount: number;
  invalidDatesFixed: number;
  emptySectorsHandled: number;
  incompleteWorkOrders: number;
  totalCleanedDeals: number;
  totalCleanedWorkOrders: number;
  logs: DataQualityLog[];
}
