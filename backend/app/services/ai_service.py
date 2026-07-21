import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from app.services.analytics_service import analytics_service
from app.services.monday_service import monday_service
from app.models.schemas import ChatResponse, FilterParams

class AIService:
    def __init__(self):
        pass

    def execute_tool(self, tool_name: str, args: Dict[str, Any], deals: List[Dict[str, Any]], work_orders: List[Dict[str, Any]]) -> Dict[str, Any]:
        if tool_name == "calculate_revenue":
            sector = args.get("sector")
            stage = args.get("stage")
            tot = 0.0
            count = 0
            for d in deals:
                if sector and sector.lower() not in d.get("sector", "").lower():
                    continue
                if stage and stage.lower() not in d.get("dealStage", "").lower():
                    continue
                tot += d.get("maskedDealValue", 0.0)
                count += 1
            return {"totalRevenue": round(tot, 2), "dealCount": count, "sector": sector, "stage": stage}

        elif tool_name == "lookup_deals":
            query = str(args.get("query", "")).lower().strip()
            status = args.get("status", "").lower()
            limit = args.get("limit", 15)
            results = []
            for d in deals:
                if status and status not in d.get("dealStatus", "").lower():
                    continue
                if query:
                    norm_query = re.sub(r'[^a-z0-9]', '', query)
                    name_norm = re.sub(r'[^a-z0-9]', '', d.get('dealName', '').lower())
                    client_norm = re.sub(r'[^a-z0-9]', '', d.get('clientCode', '').lower())
                    owner_norm = re.sub(r'[^a-z0-9]', '', d.get('ownerCode', '').lower())
                    sector_norm = re.sub(r'[^a-z0-9]', '', d.get('sector', '').lower())
                    
                    if norm_query not in name_norm and norm_query not in client_norm and norm_query not in owner_norm and norm_query not in sector_norm:
                        continue
                results.append(d)
                if len(results) >= limit:
                    break
            return {"matchedDeals": results, "count": len(results)}

        elif tool_name == "lookup_work_orders":
            status = args.get("status", "").lower()
            delayed_only = args.get("delayedOnly", False)
            query = str(args.get("query", "")).lower().strip()
            limit = args.get("limit", 15)
            results = []
            for w in work_orders:
                if delayed_only and not w.get("isDelayed", False):
                    continue
                if status and status not in w.get("executionStatus", "").lower():
                    continue
                if query:
                    norm_query = re.sub(r'[^a-z0-9]', '', query)
                    name_norm = re.sub(r'[^a-z0-9]', '', w.get('dealName', '').lower())
                    cust_norm = re.sub(r'[^a-z0-9]', '', w.get('customerNameCode', '').lower())
                    serial_norm = re.sub(r'[^a-z0-9]', '', w.get('serialNo', '').lower())
                    if norm_query not in name_norm and norm_query not in cust_norm and norm_query not in serial_norm:
                        continue
                results.append(w)
                if len(results) >= limit:
                    break
            return {"matchedWorkOrders": results, "count": len(results)}

        elif tool_name == "analyze_sectors":
            sec_map: Dict[str, float] = {}
            for d in deals:
                s = d.get("sector", "Unassigned / Other")
                sec_map[s] = sec_map.get(s, 0.0) + d.get("maskedDealValue", 0.0)
            sorted_sec = sorted(sec_map.items(), key=lambda x: x[1], reverse=True)
            top = sorted_sec[0] if sorted_sec else ("None", 0.0)
            worst = sorted_sec[-1] if sorted_sec else ("None", 0.0)
            return {
                "sectorRevenueBreakdown": dict(sorted_sec),
                "topSector": top[0],
                "topSectorRevenue": round(top[1], 2),
                "lowestSector": worst[0],
                "lowestSectorRevenue": round(worst[1], 2)
            }

        elif tool_name == "analyze_pipeline":
            stage_map: Dict[str, float] = {}
            total_val = 0.0
            for d in deals:
                st = d.get("dealStage", "Qualification")
                stage_map[st] = stage_map.get(st, 0.0) + d.get("maskedDealValue", 0.0)
                total_val += d.get("maskedDealValue", 0.0)
            return {"totalPipelineValue": round(total_val, 2), "stageBreakdown": stage_map, "totalDeals": len(deals)}

        elif tool_name == "generate_forecast":
            exp_rev = 0.0
            tot_pipe = 0.0
            for d in deals:
                tot_pipe += d.get("maskedDealValue", 0.0)
                prob = d.get("closureProbability", "Medium")
                w = 0.8 if prob == "High" else (0.5 if prob == "Medium" else 0.2)
                exp_rev += d.get("maskedDealValue", 0.0) * w
            return {
                "projectedRevenueThisQuarter": round(exp_rev * 0.4, 2),
                "projectedRevenueNextQuarter": round(exp_rev * 0.65, 2),
                "annualPipelineProjection": round(tot_pipe * 0.75, 2)
            }

        return {"status": "Tool executed", "args": args}

    def process_query(self, message: str, filters: Optional[FilterParams] = None, api_token: str = "", deal_board_id: str = "", work_board_id: str = "") -> ChatResponse:
        deals = monday_service.fetch_deals_data(api_token, deal_board_id)
        work_orders = monday_service.fetch_work_orders_data(api_token, work_board_id)

        if filters:
            deals = analytics_service.filter_deals(deals, filters)
            work_orders = analytics_service.filter_work_orders(work_orders, filters)

        msg_lower = message.lower()
        tool_calls = []
        reply_lines = []

        # Find specific question intent qualifiers
        is_status_q = "status" in msg_lower
        is_value_q = "value" in msg_lower or "amount" in msg_lower or "receivable" in msg_lower or "cost" in msg_lower or "worth" in msg_lower
        is_owner_q = "owner" in msg_lower or "person" in msg_lower or "who" in msg_lower or "bd" in msg_lower or "kam" in msg_lower
        is_prob_q = "probability" in msg_lower or "chance" in msg_lower or "likelihood" in msg_lower
        is_sector_q = "sector" in msg_lower or "industry" in msg_lower

        # Extract entities like Alias_160, WOCOMPANY_051, COMPANY089, sdpldeal-008
        entity_matches = re.findall(r'\b(?:alias|wocompany|company|owner|sdpldeal)[_#-]?\d+\b', msg_lower)
        
        # If no explicit prefixes, look for raw digits
        if not entity_matches:
            num_match = re.search(r'\b(?:company|client|customer|deal|code)?\s*(\d{2,4})\b', msg_lower)
            if num_match:
                entity_matches = [num_match.group(1)]

        if entity_matches:
            matched_deals = []
            matched_wos = []
            
            # Lookup using all extracted terms
            for ent in entity_matches:
                res_d = self.execute_tool("lookup_deals", {"query": ent}, deals, work_orders)
                res_w = self.execute_tool("lookup_work_orders", {"query": ent}, deals, work_orders)
                
                tool_calls.append({"tool": "lookup_deals", "arguments": {"query": ent}, "result": res_d})
                tool_calls.append({"tool": "lookup_work_orders", "arguments": {"query": ent}, "result": res_w})

                matched_deals.extend(res_d["matchedDeals"])
                matched_wos.extend(res_w["matchedWorkOrders"])

            # Deduplicate results
            seen_deals = set()
            dedup_deals = []
            for d in matched_deals:
                dk = (d['dealName'].lower(), d['clientCode'].lower())
                if dk not in seen_deals:
                    seen_deals.add(dk)
                    dedup_deals.append(d)

            seen_wos = set()
            dedup_wos = []
            for w in matched_wos:
                wk = w['serialNo'].lower()
                if wk not in seen_wos:
                    seen_wos.add(wk)
                    dedup_wos.append(w)

            # Formulate CONCISE direct answer based on intent
            if dedup_deals or dedup_wos:
                name_lbl = ", ".join(ent.upper() for ent in entity_matches)
                
                if is_status_q:
                    if dedup_wos:
                        for w in dedup_wos:
                            reply_lines.append(f"The execution status of **{w['dealName']}** (`{w['serialNo']}`) is **{w['executionStatus']}**.")
                    elif dedup_deals:
                        for d in dedup_deals:
                            reply_lines.append(f"The stage of **{d['dealName']}** is **{d['dealStage']}** ({d['dealStatus']}).")
                
                elif is_value_q:
                    if dedup_deals:
                        for d in dedup_deals:
                            reply_lines.append(f"The deal value of **{d['dealName']}** (`{d['clientCode']}`) is **₹{d['maskedDealValue']:,.2f}**.")
                    if dedup_wos:
                        for w in dedup_wos:
                            reply_lines.append(f"The total value of Work Order **{w['dealName']}** (`{w['serialNo']}`) is **₹{w['amountRupeesInclGST']:,.2f}** (Receivable: ₹{w['amountReceivable']:,.2f}).")
                
                elif is_owner_q:
                    if dedup_deals:
                        for d in dedup_deals:
                            reply_lines.append(f"The Owner code for **{d['dealName']}** is **{d['ownerCode']}**.")
                    if dedup_wos:
                        for w in dedup_wos:
                            reply_lines.append(f"The BD/KAM Personnel code for **{w['dealName']}** is **{w['bdPersonnelCode']}**.")
                
                elif is_prob_q:
                    if dedup_deals:
                        for d in dedup_deals:
                            reply_lines.append(f"The closure probability of **{d['dealName']}** is **{d['closureProbability']}**.")
                
                elif is_sector_q:
                    if dedup_deals:
                        for d in dedup_deals:
                            reply_lines.append(f"**{d['dealName']}** is mapped to the **{d['sector']}** sector.")
                
                else:
                    # Provide clean, brief details when no specific property is asked
                    for d in dedup_deals:
                        reply_lines.append(f"**Deal Funnel Match**: **{d['dealName']}** | Value: ₹{d['maskedDealValue']:,.2f} | Stage: `{d['dealStage']}` | Status: `{d['dealStatus']}`")
                    for w in dedup_wos:
                        reply_lines.append(f"**Work Order Match**: **{w['dealName']}** (`{w['serialNo']}`) | Status: **{w['executionStatus']}** | Receivable: ₹{w['amountReceivable']:,.2f}")
            else:
                reply_lines.append(f"No records matching **{', '.join(e.upper() for e in entity_matches)}** were found in our boards.")

        # 2. Sector Compare Intent
        elif "compare" in msg_lower and "sector" in msg_lower:
            known_sectors = ["mining", "powerline", "renewables", "telecom", "energy", "infrastructure"]
            found = [s for s in known_sectors if s in msg_lower]
            
            if len(found) >= 2:
                reply_lines.append(f"### ⚖️ Sector Comparison: {', '.join(s.capitalize() for s in found)}")
                for s in found:
                    res = self.execute_tool("calculate_revenue", {"sector": s}, deals, work_orders)
                    tool_calls.append({"tool": "calculate_revenue", "arguments": {"sector": s}, "result": res})
                    reply_lines.append(f"- **{s.capitalize()}**: ₹{res['totalRevenue']:,.2f} ({res['dealCount']} deals)")
            else:
                res = self.execute_tool("analyze_sectors", {}, deals, work_orders)
                tool_calls.append({"tool": "analyze_sectors", "arguments": {}, "result": res})
                reply_lines.append(f"Top Sector: **{res['topSector']}** (₹{res['topSectorRevenue']:,.2f}) | Worst: **{res['lowestSector']}** (₹{res['lowestSectorRevenue']:,.2f})")

        # 3. Pipeline / Stage breakdown
        elif "pipeline" in msg_lower or "stage" in msg_lower:
            res = self.execute_tool("analyze_pipeline", {}, deals, work_orders)
            tool_calls.append({"tool": "analyze_pipeline", "arguments": {}, "result": res})
            tot_cr = res["totalPipelineValue"] / 10000000.0
            reply_lines.append(f"Our active pipeline consists of **{res['totalDeals']} deals** valued at **₹{res['totalPipelineValue']:,.2f}** ({tot_cr:.2f} Cr).")

        # 4. Delayed Work Orders / Projects at Risk
        elif "delayed" in msg_lower or "risk" in msg_lower or "behind" in msg_lower:
            res = self.execute_tool("lookup_work_orders", {"delayedOnly": True}, deals, work_orders)
            tool_calls.append({"tool": "lookup_work_orders", "arguments": {"delayedOnly": True}, "result": res})
            reply_lines.append(f"We have **{res['count']} delayed work orders** currently flagged at risk.")

        # 5. Financial Forecast
        elif "forecast" in msg_lower or "projected" in msg_lower or "revenue" in msg_lower:
            res = self.execute_tool("generate_forecast", {}, deals, work_orders)
            tool_calls.append({"tool": "generate_forecast", "arguments": {}, "result": res})
            reply_lines.append(f"**Expected Revenue Forecast (This Quarter)**: ₹{res['projectedRevenueThisQuarter']:,.2f}")

        # 6. Fallback General Summary
        else:
            res1 = self.execute_tool("analyze_pipeline", {}, deals, work_orders)
            reply_lines.append(f"BI Overview: {res1['totalDeals']} deals in pipeline | Total Value: ₹{res1['totalPipelineValue']:,.2f} | Active Orders: {len(work_orders)}")

        final_reply = "\n".join(reply_lines)
        return ChatResponse(reply=final_reply, toolCalls=tool_calls)

ai_service = AIService()
