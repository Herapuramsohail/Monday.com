from datetime import datetime
from typing import Dict, List, Any
from app.services.monday_service import monday_service
from app.services.analytics_service import analytics_service
from app.models.schemas import ExecutiveSummaryResponse

class SummaryService:
    def generate_summary(self, api_token: str = "", deal_board_id: str = "", work_board_id: str = "") -> ExecutiveSummaryResponse:
        deals = monday_service.fetch_deals_data(api_token, deal_board_id)
        work_orders = monday_service.fetch_work_orders_data(api_token, work_board_id)

        dash = analytics_service.get_dashboard_data(api_token, deal_board_id, work_board_id)
        kpis = dash.kpis

        # Pipeline in Cr
        total_pipe = kpis.totalPipelineValue
        total_pipe_cr = total_pipe / 10000000.0
        exp_rev_quarter = kpis.expectedRevenue * 0.4
        exp_rev_cr = exp_rev_quarter / 10000000.0

        best_sector = dash.charts.revenueBySector[0].name if dash.charts.revenueBySector else "N/A"
        worst_sector = dash.charts.revenueBySector[-1].name if dash.charts.revenueBySector else "N/A"

        delayed_wos = [w for w in work_orders if w.get('isDelayed', False)]
        delayed_names = [f"{w.get('dealName')} ({w.get('serialNo')})" for w in delayed_wos[:5]]

        risks = [
            f"Schedule Risk: {len(delayed_wos)} Work Orders delayed across client delivery timelines.",
            f"Sector Concentration: High revenue dependency on top sector '{best_sector}'.",
            f"Unbilled Exposure: Total amount to be billed remains high across ongoing projects."
        ]

        actions = [
            f"Expedite completion for {len(delayed_wos)} delayed work orders to accelerate revenue recognition.",
            f"Diversify sales pipeline into under-penetrated sector '{worst_sector}'.",
            f"Implement bi-weekly KAM syncs on high-value open deals."
        ]

        markdown_body = f"""# 📊 Executive Business Summary

**Generated At:** {datetime.now().strftime('%B %d, %Y - %H:%M IST')}

---

### Key Financial & Operational Highlights
- **Total Pipeline Value:** ₹{total_pipe:,.2f} (**{total_pipe_cr:.2f} Cr**)
- **Active Deals:** {kpis.openDeals} Open Deals out of {kpis.totalDeals} Total Funnel Deals
- **Expected Revenue (This Quarter):** ₹{exp_rev_quarter:,.2f} (**{exp_rev_cr:.2f} Cr**)
- **Best Performing Sector:** {best_sector}
- **Worst Performing Sector:** {worst_sector}
- **Delayed Projects:** {len(delayed_wos)} Work Orders currently flagged

---

### 🚨 Major Business Risks
1. **Schedule Risk:** {len(delayed_wos)} Work Orders delayed across client delivery timelines.
2. **Sector Concentration:** High revenue reliance on `{best_sector}`.
3. **Billing Gaps:** Incomplete invoicing on milestone deliverables.

---

### 🎯 Recommended Strategic Actions
1. **Accelerate Deliveries:** Focus operations team on closing delayed projects: {', '.join(delayed_names[:3]) or 'None'}.
2. **Expand Pipeline:** Reallocate BD personnel to boost lead generation in `{worst_sector}`.
3. **Conversion Push:** Target High-probability deals currently in 'Proposal Sent' stage.
"""

        return ExecutiveSummaryResponse(
            generatedAt=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            totalPipelineFormatted=f"₹{total_pipe:,.2f} ({total_pipe_cr:.2f} Cr)",
            activeDealsCount=kpis.openDeals,
            expectedRevenueQuarterFormatted=f"₹{exp_rev_quarter:,.2f} ({exp_rev_cr:.2f} Cr)",
            bestPerformingSector=best_sector,
            worstPerformingSector=worst_sector,
            delayedProjectsCount=len(delayed_wos),
            delayedProjectNames=delayed_names,
            majorBusinessRisks=risks,
            recommendedActions=actions,
            summaryTextMarkdown=markdown_body
        )

summary_service = SummaryService()
