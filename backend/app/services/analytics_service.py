from datetime import datetime
from typing import Dict, List, Any, Optional
from app.models.schemas import (
    FilterParams, KPICards, ChartDataPoint, ChartDataset, DashboardResponse
)
from app.services.monday_service import monday_service
from app.services.cleaner_service import cleaner_service

class AnalyticsService:
    def filter_deals(self, deals: List[Dict[str, Any]], filters: Optional[FilterParams]) -> List[Dict[str, Any]]:
        if not filters:
            return deals

        filtered = []
        for d in deals:
            # Sector filter
            if filters.sector and filters.sector.lower() != 'all':
                if d.get('sector', '').lower() != filters.sector.lower():
                    continue

            # Deal Stage filter
            if filters.dealStage and filters.dealStage.lower() != 'all':
                if filters.dealStage.lower() not in d.get('dealStage', '').lower():
                    continue

            # Salesperson filter
            if filters.salesperson and filters.salesperson.lower() != 'all':
                if d.get('ownerCode', '').lower() != filters.salesperson.lower():
                    continue

            # Date Range filter
            created_dt = d.get('createdDate')
            if created_dt:
                if filters.startDate and created_dt < filters.startDate:
                    continue
                if filters.endDate and created_dt > filters.endDate:
                    continue

            filtered.append(d)
        return filtered

    def filter_work_orders(self, work_orders: List[Dict[str, Any]], filters: Optional[FilterParams]) -> List[Dict[str, Any]]:
        if not filters:
            return work_orders

        filtered = []
        for w in work_orders:
            # Sector filter
            if filters.sector and filters.sector.lower() != 'all':
                if w.get('sector', '').lower() != filters.sector.lower():
                    continue

            # Salesperson filter
            if filters.salesperson and filters.salesperson.lower() != 'all':
                if w.get('bdPersonnelCode', '').lower() != filters.salesperson.lower():
                    continue

            # Work Order Status filter
            if filters.workOrderStatus and filters.workOrderStatus.lower() != 'all':
                if filters.workOrderStatus.lower() not in w.get('executionStatus', '').lower():
                    continue

            # Customer filter
            if filters.customer and filters.customer.lower() != 'all':
                if filters.customer.lower() not in w.get('customerNameCode', '').lower():
                    continue

            # Date Range filter
            po_date = w.get('dateOfPO')
            if po_date:
                if filters.startDate and po_date < filters.startDate:
                    continue
                if filters.endDate and po_date > filters.endDate:
                    continue

            filtered.append(w)
        return filtered

    def get_dashboard_data(
        self,
        api_token: str = "",
        deal_board_id: str = "",
        work_board_id: str = "",
        filters: Optional[FilterParams] = None
    ) -> DashboardResponse:
        all_deals = monday_service.fetch_deals_data(api_token, deal_board_id)
        all_work_orders = monday_service.fetch_work_orders_data(api_token, work_board_id)

        deals = self.filter_deals(all_deals, filters)
        work_orders = self.filter_work_orders(all_work_orders, filters)

        # 1. KPI Calculations
        total_deals = len(deals)
        open_deals = sum(1 for d in deals if d.get('dealStatus', '').lower() == 'open')
        closed_won = sum(1 for d in deals if 'won' in d.get('dealStatus', '').lower() or 'closed won' in d.get('dealStatus', '').lower())
        closed_deals = sum(1 for d in deals if 'closed' in d.get('dealStatus', '').lower())

        total_pipeline_val = sum(d.get('maskedDealValue', 0.0) for d in deals)

        # Expected revenue: probability-weighted
        prob_weights = {"High": 0.8, "Medium": 0.5, "Low": 0.2}
        expected_rev = 0.0
        for d in deals:
            val = d.get('maskedDealValue', 0.0)
            if 'won' in d.get('dealStatus', '').lower():
                expected_rev += val
            elif d.get('dealStatus', '').lower() == 'open':
                weight = prob_weights.get(d.get('closureProbability', 'Medium'), 0.5)
                expected_rev += val * weight

        active_wo = sum(1 for w in work_orders if w.get('executionStatus', '').lower() in ['ongoing', 'in progress', 'executed until current month', 'proof of concept'])
        completed_wo = sum(1 for w in work_orders if w.get('executionStatus', '').lower() in ['completed', 'closed'])
        delayed_wo = sum(1 for w in work_orders if w.get('isDelayed', False))

        avg_deal_size = total_pipeline_val / max(1, total_deals)
        conversion_rate = (closed_won / max(1, total_deals)) * 100

        kpis = KPICards(
            totalDeals=total_deals,
            openDeals=open_deals,
            closedDeals=closed_deals,
            totalPipelineValue=round(total_pipeline_val, 2),
            expectedRevenue=round(expected_rev, 2),
            activeWorkOrders=active_wo,
            completedWorkOrders=completed_wo,
            delayedWorkOrders=delayed_wo,
            averageDealSize=round(avg_deal_size, 2),
            conversionRate=round(conversion_rate, 1)
        )

        # 2. Charts Calculations

        # A. Pipeline by Stage
        stage_dict: Dict[str, Dict[str, float]] = {}
        for d in deals:
            stg = d.get('dealStage', 'Qualification')
            if stg not in stage_dict:
                stage_dict[stg] = {'value': 0.0, 'count': 0}
            stage_dict[stg]['value'] += d.get('maskedDealValue', 0.0)
            stage_dict[stg]['count'] += 1

        pipeline_by_stage = [
            ChartDataPoint(name=k, value=round(v['value'], 2), count=v['count'])
            for k, v in stage_dict.items()
        ]
        pipeline_by_stage.sort(key=lambda x: x.value, reverse=True)

        # B. Revenue by Sector
        sector_dict: Dict[str, Dict[str, float]] = {}
        for d in deals:
            sec = d.get('sector', 'Unassigned / Other')
            if sec not in sector_dict:
                sector_dict[sec] = {'value': 0.0, 'count': 0}
            sector_dict[sec]['value'] += d.get('maskedDealValue', 0.0)
            sector_dict[sec]['count'] += 1

        revenue_by_sector = [
            ChartDataPoint(name=k, value=round(v['value'], 2), count=v['count'])
            for k, v in sector_dict.items()
        ]
        revenue_by_sector.sort(key=lambda x: x.value, reverse=True)

        # C. Revenue by Salesperson
        owner_dict: Dict[str, Dict[str, float]] = {}
        for d in deals:
            own = d.get('ownerCode', 'OWNER_UNKNOWN')
            if own not in owner_dict:
                owner_dict[own] = {'value': 0.0, 'count': 0}
            owner_dict[own]['value'] += d.get('maskedDealValue', 0.0)
            owner_dict[own]['count'] += 1

        revenue_by_salesperson = [
            ChartDataPoint(name=k, value=round(v['value'], 2), count=v['count'])
            for k, v in owner_dict.items()
        ]
        revenue_by_salesperson.sort(key=lambda x: x.value, reverse=True)

        # D. Deals by Month
        month_dict: Dict[str, Dict[str, float]] = {}
        for d in deals:
            dt_str = d.get('createdDate') or d.get('tentativeCloseDate')
            if dt_str and len(dt_str) >= 7:
                m_key = dt_str[:7]
            else:
                m_key = "2025-12"
            if m_key not in month_dict:
                month_dict[m_key] = {'value': 0.0, 'count': 0}
            month_dict[m_key]['value'] += d.get('maskedDealValue', 0.0)
            month_dict[m_key]['count'] += 1

        deals_by_month = [
            ChartDataPoint(name=k, value=round(v['value'], 2), count=v['count'])
            for k, v in sorted(month_dict.items())
        ]

        # E. Work Orders by Status
        wo_status_dict: Dict[str, int] = {}
        for w in work_orders:
            st = w.get('executionStatus', 'Not Started')
            wo_status_dict[st] = wo_status_dict.get(st, 0) + 1

        work_orders_by_status = [
            ChartDataPoint(name=k, value=float(v), count=v)
            for k, v in wo_status_dict.items()
        ]

        # F. Project Completion Trend
        comp_trend_dict: Dict[str, int] = {}
        for w in work_orders:
            dt_str = w.get('dataDeliveryDate') or w.get('probableEndDate')
            if dt_str and len(dt_str) >= 7:
                m_key = dt_str[:7]
                comp_trend_dict[m_key] = comp_trend_dict.get(m_key, 0) + 1

        project_completion_trend = [
            ChartDataPoint(name=k, value=float(v), count=v)
            for k, v in sorted(comp_trend_dict.items())
        ]

        # G. Sector Distribution
        sector_distribution = revenue_by_sector[:8]

        # H. Revenue Forecast
        # Simple projection based on weighted pipeline
        forecast_points = [
            ChartDataPoint(name="Current Qtr", value=round(expected_rev * 0.4, 2)),
            ChartDataPoint(name="Q+1 Forecast", value=round(expected_rev * 0.65, 2)),
            ChartDataPoint(name="Q+2 Forecast", value=round(expected_rev * 0.85, 2)),
            ChartDataPoint(name="Q+3 Forecast", value=round(total_pipeline_val * 0.45, 2)),
            ChartDataPoint(name="Annual Projection", value=round(total_pipeline_val * 0.75, 2))
        ]

        charts = ChartDataset(
            pipelineByStage=pipeline_by_stage,
            revenueBySector=revenue_by_sector,
            revenueBySalesperson=revenue_by_salesperson,
            dealsByMonth=deals_by_month,
            workOrdersByStatus=work_orders_by_status,
            projectCompletionTrend=project_completion_trend,
            sectorDistribution=sector_distribution,
            revenueForecast=forecast_points
        )

        # Unique Filter Values
        sectors = sorted(list(set(d.get('sector', '') for d in all_deals if d.get('sector'))))
        salespersons = sorted(list(set(d.get('ownerCode', '') for d in all_deals if d.get('ownerCode'))))
        deal_stages = sorted(list(set(d.get('dealStage', '') for d in all_deals if d.get('dealStage'))))
        wo_statuses = sorted(list(set(w.get('executionStatus', '') for w in all_work_orders if w.get('executionStatus'))))
        customers = sorted(list(set(w.get('customerNameCode', '') for w in all_work_orders if w.get('customerNameCode'))))

        confidence_score = cleaner_service.get_confidence_score(len(all_deals), len(all_work_orders))

        return DashboardResponse(
            kpis=kpis,
            charts=charts,
            sectors=sectors,
            salespersons=salespersons,
            dealStages=deal_stages,
            workOrderStatuses=wo_statuses,
            customers=customers,
            dataConfidenceScore=confidence_score,
            totalRecords=len(all_deals) + len(all_work_orders)
        )

    def global_search(self, query: str, api_token: str = "", deal_board_id: str = "", work_board_id: str = "") -> Dict[str, Any]:
        q = query.lower().strip()
        if not q:
            return {"deals": [], "workOrders": []}

        all_deals = monday_service.fetch_deals_data(api_token, deal_board_id)
        all_work_orders = monday_service.fetch_work_orders_data(api_token, work_board_id)

        matching_deals = []
        for d in all_deals:
            text = f"{d.get('dealName')} {d.get('clientCode')} {d.get('ownerCode')} {d.get('sector')} {d.get('productDeal')} {d.get('dealStage')}".lower()
            if q in text:
                matching_deals.append(d)

        matching_wo = []
        for w in all_work_orders:
            text = f"{w.get('dealName')} {w.get('customerNameCode')} {w.get('serialNo')} {w.get('bdPersonnelCode')} {w.get('sector')} {w.get('typeOfWork')} {w.get('natureOfWork')}".lower()
            if q in text:
                matching_wo.append(w)

        return {
            "deals": matching_deals[:20],
            "workOrders": matching_wo[:20]
        }

analytics_service = AnalyticsService()
