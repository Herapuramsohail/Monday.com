"""
Monday.com AI BI Agent - Zero-dependency HTTP server.
Uses only Python standard library (no pydantic, no fastapi, no requests).
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# ---------------------------------------------------------------------------
# Load services (all stdlib-only, no pydantic)
# ---------------------------------------------------------------------------
from app.services.monday_service import monday_service
from app.services.cleaner_service import cleaner_service

# ---------------------------------------------------------------------------
# Inline analytics helpers (no pydantic models)
# ---------------------------------------------------------------------------

def _filter_deals(deals, filters):
    """Apply optional filter dict to deal list."""
    if not filters:
        return deals
    out = []
    for d in deals:
        if filters.get("sector") and filters["sector"].lower() not in ("all", "") and filters["sector"].lower() not in d.get("sector", "").lower():
            continue
        if filters.get("dealStage") and filters["dealStage"].lower() not in ("all", "") and filters["dealStage"].lower() not in d.get("dealStage", "").lower():
            continue
        if filters.get("salesperson") and filters["salesperson"].lower() not in ("all", "") and filters["salesperson"].lower() not in d.get("ownerCode", "").lower():
            continue
        if filters.get("startDate"):
            if d.get("expectedCloseDate", "") < filters["startDate"]:
                continue
        if filters.get("endDate"):
            if d.get("expectedCloseDate", "") > filters["endDate"]:
                continue
        out.append(d)
    return out


def _filter_work_orders(work_orders, filters):
    """Apply optional filter dict to work order list."""
    if not filters:
        return work_orders
    out = []
    for w in work_orders:
        if filters.get("workOrderStatus") and filters["workOrderStatus"].lower() not in ("all", "") and filters["workOrderStatus"].lower() not in w.get("executionStatus", "").lower():
            continue
        if filters.get("customer") and filters["customer"].lower() not in ("all", "") and filters["customer"].lower() not in w.get("customerNameCode", "").lower():
            continue
        out.append(w)
    return out


def _build_dashboard(deals, work_orders):
    """Compute KPIs and chart data as plain dicts."""
    total_pipeline = sum(d.get("maskedDealValue", 0) for d in deals)
    won = [d for d in deals if d.get("dealStatus", "").lower() in ("won", "closed won")]
    won_rev = sum(d.get("maskedDealValue", 0) for d in won)

    # Sector breakdown
    sec_map = {}
    for d in deals:
        s = d.get("sector", "Other")
        sec_map[s] = sec_map.get(s, 0) + d.get("maskedDealValue", 0)

    # Stage breakdown
    stage_map = {}
    for d in deals:
        st = d.get("dealStage", "Qualification")
        stage_map[st] = stage_map.get(st, 0) + 1

    # Work order status
    wo_status = {}
    for w in work_orders:
        s = w.get("executionStatus", "Unknown")
        wo_status[s] = wo_status.get(s, 0) + 1

    delayed = [w for w in work_orders if w.get("isDelayed", False)]

    # Revenue forecast (simple weighted projection)
    exp_rev = 0
    for d in deals:
        prob = d.get("closureProbability", "Medium")
        w = 0.8 if prob == "High" else (0.5 if prob == "Medium" else 0.2)
        exp_rev += d.get("maskedDealValue", 0) * w

    return {
        "kpis": {
            "totalPipelineValue": round(total_pipeline, 2),
            "wonRevenue": round(won_rev, 2),
            "totalDeals": len(deals),
            "wonDeals": len(won),
            "activeWorkOrders": len(work_orders),
            "delayedWorkOrders": len(delayed),
            "expectedRevenue": round(exp_rev, 2),
            "winRate": round(len(won) / len(deals) * 100, 1) if deals else 0
        },
        "charts": {
            "sectorBreakdown": [{"sector": k, "value": round(v, 2)} for k, v in sorted(sec_map.items(), key=lambda x: x[1], reverse=True)],
            "stagePipeline": [{"stage": k, "count": v} for k, v in stage_map.items()],
            "workOrderStatus": [{"status": k, "count": v} for k, v in wo_status.items()],
            "revenueForecast": [
                {"quarter": "Q1 2025", "projected": round(exp_rev * 0.25, 2), "actual": round(won_rev * 0.3, 2)},
                {"quarter": "Q2 2025", "projected": round(exp_rev * 0.35, 2), "actual": round(won_rev * 0.4, 2)},
                {"quarter": "Q3 2025", "projected": round(exp_rev * 0.45, 2), "actual": round(won_rev * 0.5, 2)},
                {"quarter": "Q4 2025", "projected": round(exp_rev * 0.6, 2), "actual": 0}
            ]
        }
    }


# ---------------------------------------------------------------------------
# Inline AI query processor (no pydantic)
# ---------------------------------------------------------------------------
import re

def _process_chat(message, deals, work_orders):
    """
    Parse the user message and return a concise, direct answer dict.
    Returns: {"reply": "...", "toolCalls": [...]}
    """
    msg_lower = message.lower().strip()
    tool_calls = []
    reply_lines = []

    # Intent flags
    is_status = any(w in msg_lower for w in ["status", "execution", "state", "progress"])
    is_value  = any(w in msg_lower for w in ["value", "amount", "worth", "cost", "receivable", "price", "revenue", "deal value"])
    is_owner  = any(w in msg_lower for w in ["owner", "who", "person", "bd", "kam", "personnel"])
    is_prob   = any(w in msg_lower for w in ["probability", "chance", "likelihood", "closure"])
    is_sector = any(w in msg_lower for w in ["sector", "industry", "vertical"])
    is_stage  = any(w in msg_lower for w in ["stage", "pipeline", "funnel"])
    is_delayed = any(w in msg_lower for w in ["delayed", "overdue", "late", "behind", "risk"])
    is_forecast = any(w in msg_lower for w in ["forecast", "project", "quarterly", "annual"])

    # -----------------------------------------------------------------------
    # Extract entity codes: Alias_160, WOCOMPANY_051, COMPANY089, SDPLDEAL-008, owner_001 etc.
    # -----------------------------------------------------------------------
    entity_pattern = re.compile(
        r'\b(?:alias_?\d+|wocompany_?\d+|company\d+|owner_?\d+|sdpldeal[-_]?\d+|deal[-_]?\d+|wo[-_]?\d+)\b',
        re.IGNORECASE
    )
    entities = entity_pattern.findall(message)
    # Also catch bare 3–4 digit numbers that might be entity references
    if not entities:
        bare_num = re.search(r'\b(\d{3,4})\b', msg_lower)
        if bare_num:
            entities = [bare_num.group(1)]

    def norm(s):
        return re.sub(r'[^a-z0-9]', '', s.lower())

    def match_deals(query_norm):
        found = []
        for d in deals:
            fields = [d.get('dealName',''), d.get('clientCode',''), d.get('ownerCode',''), d.get('sector','')]
            if any(query_norm in norm(f) for f in fields):
                found.append(d)
        return found

    def match_work_orders(query_norm):
        found = []
        for w in work_orders:
            fields = [w.get('dealName',''), w.get('customerNameCode',''), w.get('serialNo',''), w.get('bdPersonnelCode','')]
            if any(query_norm in norm(f) for f in fields):
                found.append(w)
        return found

    # -----------------------------------------------------------------------
    # Entity-based lookup — INTERSECT when multiple entities given
    # -----------------------------------------------------------------------
    if entities:
        # For each entity, get the set of matching serial nos / deal keys
        wo_sets = []
        d_sets = []

        for ent in entities:
            q = norm(ent)
            md = match_deals(q)
            mw = match_work_orders(q)
            tool_calls.append({"tool": "lookup_deals", "arguments": {"query": ent}, "result": {"count": len(md)}})
            tool_calls.append({"tool": "lookup_work_orders", "arguments": {"query": ent}, "result": {"count": len(mw)}})
            wo_sets.append({norm(w.get('serialNo','')): w for w in mw})
            d_sets.append({norm(d.get('dealName','') + d.get('clientCode','')): d for d in md})

        # Intersect: keep only keys present in ALL sets (records matching every entity term)
        if len(wo_sets) > 1:
            common_wo_keys = set(wo_sets[0].keys())
            for s in wo_sets[1:]:
                common_wo_keys &= set(s.keys())
            dedup_w = [wo_sets[0][k] for k in common_wo_keys]
        else:
            dedup_w = list(wo_sets[0].values()) if wo_sets else []

        if len(d_sets) > 1:
            common_d_keys = set(d_sets[0].keys())
            for s in d_sets[1:]:
                common_d_keys &= set(s.keys())
            dedup_d = [d_sets[0][k] for k in common_d_keys]
        else:
            dedup_d = list(d_sets[0].values()) if d_sets else []

        # If intersection is empty, fall back to union from the most specific entity (last one)
        if not dedup_w and not dedup_d:
            # Try union approach across all entities
            all_w = {}
            all_d = {}
            for ws in wo_sets:
                all_w.update(ws)
            for ds in d_sets:
                all_d.update(ds)
            dedup_w = list(all_w.values())
            dedup_d = list(all_d.values())

        if not dedup_d and not dedup_w:
            reply_lines.append(f"No records found for **{', '.join(entities)}**.")
        else:
            entity_label = ', '.join(entities)

            # ---- STATUS question ----
            if is_status:
                if dedup_w:
                    if len(dedup_w) == 1:
                        w = dedup_w[0]
                        reply_lines.append(f"**{w['dealName']}** (`{w['serialNo']}`) — Execution Status: **{w['executionStatus']}**")
                    else:
                        # Group by status for concise summary
                        status_counts = {}
                        for w in dedup_w:
                            s = w.get('executionStatus','Unknown')
                            status_counts[s] = status_counts.get(s, 0) + 1
                        summary_parts = [f"{cnt} {st}" for st, cnt in sorted(status_counts.items(), key=lambda x: x[1], reverse=True)]
                        name = dedup_w[0]['dealName']
                        reply_lines.append(f"**{name}** (`{entity_label}`) has **{len(dedup_w)} work orders**: {', '.join(summary_parts)}.")
                elif dedup_d:
                    if len(dedup_d) == 1:
                        d = dedup_d[0]
                        reply_lines.append(f"**{d['dealName']}** — Stage: **{d['dealStage']}** | Status: **{d['dealStatus']}**")
                    else:
                        stage_counts = {}
                        for d in dedup_d:
                            s = d.get('dealStage','Unknown')
                            stage_counts[s] = stage_counts.get(s, 0) + 1
                        parts = [f"{cnt} {st}" for st, cnt in sorted(stage_counts.items(), key=lambda x: x[1], reverse=True)]
                        reply_lines.append(f"**{entity_label}** deals: {', '.join(parts)}.")

            # ---- VALUE question ----
            elif is_value:
                if dedup_d:
                    if len(dedup_d) == 1:
                        d = dedup_d[0]
                        reply_lines.append(f"**{d['dealName']}** (`{d['clientCode']}`) — Deal Value: **INR {d['maskedDealValue']:,.2f}**")
                    else:
                        total = sum(d.get('maskedDealValue',0) for d in dedup_d)
                        reply_lines.append(f"**{entity_label}** — Total Deal Value across {len(dedup_d)} deals: **INR {total:,.2f}**")
                if dedup_w:
                    total_recv = sum(w.get('amountReceivable',0) for w in dedup_w)
                    if len(dedup_w) == 1:
                        w = dedup_w[0]
                        reply_lines.append(f"**{w['dealName']}** (`{w['serialNo']}`) — Receivable: **INR {w.get('amountReceivable',0):,.2f}**")
                    else:
                        reply_lines.append(f"**{entity_label}** — Total Receivable across {len(dedup_w)} orders: **INR {total_recv:,.2f}**")

            # ---- OWNER question ----
            elif is_owner:
                if dedup_d:
                    owners = list({d.get('ownerCode','N/A') for d in dedup_d})
                    reply_lines.append(f"**{entity_label}** — Owner: **{', '.join(owners)}**")
                if dedup_w:
                    kams = list({w.get('bdPersonnelCode','N/A') for w in dedup_w})
                    reply_lines.append(f"**{entity_label}** — BD/KAM Personnel: **{', '.join(kams)}**")

            # ---- PROBABILITY question ----
            elif is_prob:
                if dedup_d:
                    probs = list({d.get('closureProbability','N/A') for d in dedup_d})
                    reply_lines.append(f"**{entity_label}** — Closure Probability: **{', '.join(probs)}**")

            # ---- SECTOR question ----
            elif is_sector:
                if dedup_d:
                    sectors = list({d.get('sector','N/A') for d in dedup_d})
                    reply_lines.append(f"**{entity_label}** — Sector: **{', '.join(sectors)}**")

            # ---- STAGE question ----
            elif is_stage:
                if dedup_d:
                    stages = list({d.get('dealStage','N/A') for d in dedup_d})
                    reply_lines.append(f"**{entity_label}** — Stage: **{', '.join(stages)}**")

            # ---- Generic lookup — compact summary ----
            else:
                for d in dedup_d[:3]:
                    reply_lines.append(
                        f"**{d['dealName']}** | Value: INR {d['maskedDealValue']:,.2f} | "
                        f"Stage: {d['dealStage']} | Status: {d['dealStatus']}"
                    )
                for w in dedup_w[:3]:
                    reply_lines.append(
                        f"**{w['dealName']}** (`{w['serialNo']}`) | "
                        f"Status: {w['executionStatus']} | Customer: {w['customerNameCode']}"
                    )

    # -----------------------------------------------------------------------
    # Sector comparison
    # -----------------------------------------------------------------------
    elif "compare" in msg_lower and is_sector:
        known = ["mining", "powerline", "renewables", "telecom", "energy", "infrastructure"]
        found_sectors = [s for s in known if s in msg_lower]
        if len(found_sectors) >= 2:
            for s in found_sectors:
                tot = sum(d.get("maskedDealValue",0) for d in deals if s.lower() in d.get("sector","").lower())
                cnt = sum(1 for d in deals if s.lower() in d.get("sector","").lower())
                reply_lines.append(f"**{s.capitalize()}**: INR {tot:,.2f} ({cnt} deals)")
        else:
            sec_map = {}
            for d in deals:
                s = d.get("sector","Other")
                sec_map[s] = sec_map.get(s,0) + d.get("maskedDealValue",0)
            top = sorted(sec_map.items(), key=lambda x:x[1], reverse=True)
            for s, v in top[:5]:
                reply_lines.append(f"**{s}**: INR {v:,.2f}")

    # -----------------------------------------------------------------------
    # Delayed work orders
    # -----------------------------------------------------------------------
    elif is_delayed:
        delayed = [w for w in work_orders if w.get("isDelayed", False)]
        tool_calls.append({"tool":"lookup_work_orders","arguments":{"delayedOnly":True},"result":{"count":len(delayed)}})
        reply_lines.append(f"There are **{len(delayed)} delayed work orders** currently at risk.")
        for w in delayed[:5]:
            reply_lines.append(f"- **{w['dealName']}** (`{w['serialNo']}`) — {w['executionStatus']}")

    # -----------------------------------------------------------------------
    # Revenue forecast
    # -----------------------------------------------------------------------
    elif is_forecast:
        exp = sum(d.get("maskedDealValue",0) * (0.8 if d.get("closureProbability")=="High" else 0.5 if d.get("closureProbability")=="Medium" else 0.2) for d in deals)
        tool_calls.append({"tool":"generate_forecast","arguments":{},"result":{"expectedRevenue": round(exp,2)}})
        reply_lines.append(f"Projected revenue this quarter: **INR {exp*0.4:,.2f}**")
        reply_lines.append(f"Next quarter projection: **INR {exp*0.65:,.2f}**")

    # -----------------------------------------------------------------------
    # Pipeline / stage overview
    # -----------------------------------------------------------------------
    elif is_stage or "pipeline" in msg_lower:
        tot = sum(d.get("maskedDealValue",0) for d in deals)
        tool_calls.append({"tool":"analyze_pipeline","arguments":{},"result":{"totalDeals":len(deals),"total":tot}})
        reply_lines.append(f"Pipeline: **{len(deals)} deals** | Total Value: INR {tot:,.2f}")

    # -----------------------------------------------------------------------
    # Fallback
    # -----------------------------------------------------------------------
    else:
        tot = sum(d.get("maskedDealValue",0) for d in deals)
        reply_lines.append(f"Active pipeline: **{len(deals)} deals** | Value: INR {tot:,.2f} | Work Orders: {len(work_orders)}")
        reply_lines.append("Try asking: *'What is the status of Alias_160?'* or *'Deal value of COMPANY089?'*")

    return {"reply": "\n".join(reply_lines), "toolCalls": tool_calls}


# ---------------------------------------------------------------------------
# HTTP Handler
# ---------------------------------------------------------------------------

class BIRequestHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        # Suppress default access log to avoid encoding issues on Windows
        pass

    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        def g(k):
            return params[k][0] if k in params and params[k] else ""

        try:
            if path == "/health":
                self._ok({"status": "healthy", "service": "Monday.com AI BI Agent", "version": "2.0.0"})

            elif path == "/dashboard":
                filters = {
                    "startDate": g("startDate") or None,
                    "endDate": g("endDate") or None,
                    "sector": g("sector") or None,
                    "dealStage": g("dealStage") or None,
                    "salesperson": g("salesperson") or None,
                    "workOrderStatus": g("workOrderStatus") or None,
                    "customer": g("customer") or None
                }
                deals = monday_service.fetch_deals_data(g("apiToken"), g("dealBoardId"))
                work_orders = monday_service.fetch_work_orders_data(g("apiToken"), g("workBoardId"))
                deals = _filter_deals(deals, filters)
                work_orders = _filter_work_orders(work_orders, filters)
                self._ok(_build_dashboard(deals, work_orders))

            elif path == "/deals":
                filters = {
                    "sector": g("sector") or None,
                    "dealStage": g("dealStage") or None,
                    "salesperson": g("salesperson") or None,
                    "startDate": g("startDate") or None,
                    "endDate": g("endDate") or None
                }
                deals = monday_service.fetch_deals_data(g("apiToken"), g("dealBoardId"))
                deals = _filter_deals(deals, filters)
                self._ok({"deals": deals, "count": len(deals)})

            elif path == "/workorders":
                filters = {
                    "workOrderStatus": g("workOrderStatus") or None,
                    "customer": g("customer") or None
                }
                work_orders = monday_service.fetch_work_orders_data(g("apiToken"), g("workBoardId"))
                work_orders = _filter_work_orders(work_orders, filters)
                self._ok({"workOrders": work_orders, "count": len(work_orders)})

            elif path == "/data-quality":
                deals = monday_service.fetch_deals_data(g("apiToken"), g("dealBoardId"))
                work_orders = monday_service.fetch_work_orders_data(g("apiToken"), g("workBoardId"))
                score = cleaner_service.get_confidence_score(len(deals), len(work_orders))
                self._ok({
                    "confidenceScore": score,
                    "missingValuesCount": cleaner_service._missing_count,
                    "duplicateRecordsCount": cleaner_service._duplicate_count,
                    "invalidDatesFixed": cleaner_service._date_fix_count,
                    "emptySectorsHandled": cleaner_service._sector_fix_count,
                    "incompleteWorkOrders": cleaner_service._incomplete_work_orders,
                    "totalCleanedDeals": len(deals),
                    "totalCleanedWorkOrders": len(work_orders)
                })

            elif path == "/search":
                q = g("query")
                deals = monday_service.fetch_deals_data(g("apiToken"), g("dealBoardId"))
                work_orders = monday_service.fetch_work_orders_data(g("apiToken"), g("workBoardId"))
                q_norm = re.sub(r'[^a-z0-9]', '', q.lower())

                def nm(s): return re.sub(r'[^a-z0-9]', '', s.lower())
                deal_hits = [d for d in deals if any(q_norm in nm(d.get(f,'')) for f in ['dealName','clientCode','ownerCode','sector'])]
                wo_hits = [w for w in work_orders if any(q_norm in nm(w.get(f,'')) for f in ['dealName','customerNameCode','serialNo'])]
                self._ok({"deals": deal_hits[:20], "workOrders": wo_hits[:20], "totalResults": len(deal_hits)+len(wo_hits)})

            else:
                self._err(404, "Endpoint not found")
        except Exception as e:
            self._err(500, str(e))

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        content_length = int(self.headers.get('Content-Length', 0))
        body_bytes = self.rfile.read(content_length) if content_length > 0 else b'{}'
        try:
            body = json.loads(body_bytes.decode('utf-8'))
        except Exception:
            body = {}

        try:
            if path == "/chat":
                msg = body.get("message", "")
                api_token = body.get("apiToken", "")
                deal_board_id = body.get("dealBoardId", "")
                work_board_id = body.get("workBoardId", "")

                deals = monday_service.fetch_deals_data(api_token, deal_board_id)
                work_orders = monday_service.fetch_work_orders_data(api_token, work_board_id)

                # Apply filters if provided
                filters = body.get("filters")
                if filters:
                    deals = _filter_deals(deals, filters)
                    work_orders = _filter_work_orders(work_orders, filters)

                result = _process_chat(msg, deals, work_orders)
                self._ok(result)

            elif path == "/summary":
                api_token = body.get("apiToken", "")
                deal_board_id = body.get("dealBoardId", "")
                work_board_id = body.get("workBoardId", "")
                deals = monday_service.fetch_deals_data(api_token, deal_board_id)
                work_orders = monday_service.fetch_work_orders_data(api_token, work_board_id)
                db = _build_dashboard(deals, work_orders)
                kpis = db["kpis"]
                top_sectors = db["charts"]["sectorBreakdown"][:3]
                delayed_count = kpis["delayedWorkOrders"]

                # Executive summary text
                summary_text = (
                    f"Pipeline has {kpis['totalDeals']} deals worth INR {kpis['totalPipelineValue']:,.2f}. "
                    f"Win rate: {kpis['winRate']}%. "
                    f"Expected revenue: INR {kpis['expectedRevenue']:,.2f}. "
                    f"Top sectors: {', '.join(s['sector'] for s in top_sectors)}. "
                    f"Delayed work orders: {delayed_count}."
                )
                self._ok({"summary": summary_text, "kpis": kpis})

            elif path == "/forecast":
                api_token = body.get("apiToken", "")
                deal_board_id = body.get("dealBoardId", "")
                work_board_id = body.get("workBoardId", "")
                deals = monday_service.fetch_deals_data(api_token, deal_board_id)
                work_orders = monday_service.fetch_work_orders_data(api_token, work_board_id)
                db = _build_dashboard(deals, work_orders)
                self._ok({"forecast": db["charts"]["revenueForecast"], "expectedRevenue": db["kpis"]["expectedRevenue"]})

            elif path == "/settings/verify":
                token = body.get("mondayApiToken", "")
                deal_id = body.get("dealBoardId", "")
                work_id = body.get("workBoardId", "")
                success, msg, details = monday_service.verify_connection(token, deal_id, work_id)
                self._ok({
                    "success": success,
                    "message": msg,
                    "dealBoardName": details.get("dealBoardName"),
                    "workBoardName": details.get("workBoardName"),
                    "dealItemsCount": details.get("dealItemsCount", 0),
                    "workItemsCount": details.get("workItemsCount", 0)
                })
            else:
                self._err(404, "Endpoint not found")
        except Exception as e:
            self._err(500, str(e))

    def _ok(self, data):
        self._respond_json(200, data)

    def _err(self, code, msg):
        self._respond_json(code, {"error": msg})

    def _respond_json(self, status_code, data):
        body = json.dumps(data, indent=2, default=str).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(body)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run_server(port=None):
    if port is None:
        port = int(os.environ.get("PORT", 8000))
    server_address = ('', port)
    httpd = HTTPServer(server_address, BIRequestHandler)
    sys.stdout.write(f"BI Server running on port {port}\n")
    sys.stdout.flush()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        sys.stdout.write("\nServer stopped.\n")


if __name__ == '__main__':
    run_server()
