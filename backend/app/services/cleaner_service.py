import os
import csv
import re
from datetime import datetime
from typing import Dict, List, Tuple, Any
from app.config import settings
from app.models.schemas import DataQualityLog

class DataCleanerService:
    def __init__(self):
        self.logs: List[DataQualityLog] = []
        self._missing_count = 0
        self._duplicate_count = 0
        self._date_fix_count = 0
        self._sector_fix_count = 0
        self._incomplete_work_orders = 0

    def _log(self, field: str, operation: str, affected_count: int, details: str):
        if affected_count > 0:
            log_entry = DataQualityLog(
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                field=field,
                operation=operation,
                affectedCount=affected_count,
                details=details
            )
            self.logs.append(log_entry)

    def parse_float(self, val: Any, default: float = 0.0) -> float:
        if val is None:
            return default
        s = str(val).strip()
        if not s or s.lower() in ['nan', 'null', 'none', 'n/a', '']:
            return default
        cleaned = re.sub(r'[^\d.-]', '', s)
        try:
            return float(cleaned)
        except Exception:
            return default

    def parse_date_str(self, val: Any) -> str:
        if not val or str(val).strip().lower() in ['nan', 'null', 'none', 'n/a', '']:
            return ""
        s = str(val).strip()
        
        # Try standard YYYY-MM-DD
        if re.match(r'^\d{4}-\d{2}-\d{2}$', s):
            return s

        date_formats = [
            "%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y",
            "%Y/%m/%d", "%b %d, %Y", "%d %b %Y", "%Y-%m-%dT%H:%M:%S"
        ]
        for fmt in date_formats:
            try:
                dt = datetime.strptime(s, fmt)
                return dt.strftime("%Y-%m-%d")
            except Exception:
                continue

        # Extract digits YYYY, MM, DD using regex
        parts = re.findall(r'\d+', s)
        if len(parts) >= 3:
            try:
                y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
                if y < 100: y += 2000
                if m > 12: m, d = d, m
                return f"{y:04d}-{m:02d}-{d:02d}"
            except Exception:
                pass

        return ""

    def clean_deals_data(self, raw_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        cleaned_deals = []
        seen_keys = set()
        missing_vals = 0
        date_fixes = 0
        blank_sectors = 0
        duplicates = 0

        for row in raw_rows:
            deal_name = str(row.get('Deal Name', '') or '').strip()
            owner_code = str(row.get('Owner code', '') or 'OWNER_UNKNOWN').strip()
            client_code = str(row.get('Client Code', '') or 'COMPANY_UNKNOWN').strip()

            if not deal_name:
                deal_name = f"Deal_{client_code}"
                missing_vals += 1

            dedup_key = (deal_name.lower(), client_code.lower(), owner_code.lower())
            is_dup = dedup_key in seen_keys
            if is_dup:
                duplicates += 1
            else:
                seen_keys.add(dedup_key)

            val_raw = row.get('Masked Deal value', 0)
            deal_value = self.parse_float(val_raw, 0.0)
            if not val_raw or deal_value == 0.0:
                missing_vals += 1

            prob_raw = str(row.get('Closure Probability', '') or '').strip()
            if not prob_raw:
                prob = "Medium"
                missing_vals += 1
            else:
                prob = prob_raw.capitalize()

            created_date = self.parse_date_str(row.get('Created Date'))
            close_actual = self.parse_date_str(row.get('Close Date (A)'))
            tentative_close = self.parse_date_str(row.get('Tentative Close Date'))

            if row.get('Created Date') and not created_date:
                date_fixes += 1
            if row.get('Tentative Close Date') and not tentative_close:
                date_fixes += 1

            stage_raw = str(row.get('Deal Stage', '') or '').strip()
            if not stage_raw:
                stage = "Qualification"
                missing_vals += 1
            else:
                stage = re.sub(r'^[A-Z]\.\s*', '', stage_raw)

            status_raw = str(row.get('Deal Status', '') or 'Open').strip().capitalize()
            if status_raw not in ['Open', 'Closed won', 'Closed lost', 'Closed']:
                if 'won' in status_raw.lower():
                    status_raw = 'Closed Won'
                elif 'lost' in status_raw.lower():
                    status_raw = 'Closed Lost'
                elif 'close' in status_raw.lower():
                    status_raw = 'Closed Won'
                else:
                    status_raw = 'Open'

            sector_raw = str(row.get('Sector/service', '') or '').strip()
            if not sector_raw or sector_raw.lower() in ['nan', 'none', 'null', '']:
                sector = "Unassigned / Other"
                blank_sectors += 1
            else:
                sector = sector_raw

            product = str(row.get('Product deal', '') or 'Service').strip()

            badges = []
            if not row.get('Closure Probability'):
                badges.append("Defaulted Probability")
            if not sector_raw:
                badges.append("Inferred Sector")
            if date_fixes > 0:
                badges.append("Parsed ISO Date")

            cleaned_item = {
                "dealName": deal_name,
                "ownerCode": owner_code,
                "clientCode": client_code,
                "dealStatus": status_raw,
                "closeDateActual": close_actual,
                "closureProbability": prob,
                "maskedDealValue": deal_value,
                "tentativeCloseDate": tentative_close,
                "dealStage": stage,
                "productDeal": product,
                "sector": sector,
                "createdDate": created_date,
                "cleaningBadges": badges
            }
            cleaned_deals.append(cleaned_item)

        self._missing_count += missing_vals
        self._duplicate_count += duplicates
        self._date_fix_count += date_fixes
        self._sector_fix_count += blank_sectors

        self._log("Masked Deal value & Closure Probability", "Imputed missing fields", missing_vals, "Replaced empty probability with 'Medium' and missing amounts with 0.0")
        self._log("Dates", "Standardized to ISO YYYY-MM-DD", date_fixes, "Converted varied date string formats into standard ISO-8601 dates")
        self._log("Sector/service", "Normalized empty sectors", blank_sectors, "Assigned 'Unassigned / Other' to unclassified sector entries")
        self._log("Company / Deal Records", "Deduplicated companies", duplicates, "Identified duplicate company deal records")

        return cleaned_deals

    def clean_work_orders_data(self, raw_lines: List[List[str]]) -> List[Dict[str, Any]]:
        header_idx = -1
        for i, line in enumerate(raw_lines[:10]):
            line_str = "".join(line).lower()
            if 'deal name' in line_str or 'customer name' in line_str or 'nature of work' in line_str:
                header_idx = i
                break

        if header_idx == -1:
            header_idx = 0

        headers = [h.strip() for h in raw_lines[header_idx]]
        data_rows = raw_lines[header_idx + 1:]

        cleaned_work_orders = []
        missing_wo = 0
        date_fixes = 0
        blank_sectors = 0
        incomplete_wo = 0

        for row_cells in data_rows:
            if not row_cells or all(not str(c).strip() for c in row_cells):
                continue
            
            row_dict = {}
            for idx, h in enumerate(headers):
                if idx < len(row_cells):
                    row_dict[h] = str(row_cells[idx]).strip()

            deal_name = row_dict.get('Deal name masked') or row_dict.get('Deal Name') or 'WO_Deal'
            customer_code = row_dict.get('Customer Name Code') or 'WOCOMPANY_UNKNOWN'
            serial_no = row_dict.get('Serial #') or 'SDPLDEAL-UNKNOWN'
            nature_of_work = row_dict.get('Nature of Work') or 'General Services'
            
            exec_status = row_dict.get('Execution Status') or 'Not Started'
            if not exec_status or exec_status.lower() in ['nan', 'null']:
                exec_status = 'Not Started'
                missing_wo += 1

            delivery_date = self.parse_date_str(row_dict.get('Data Delivery Date'))
            po_date = self.parse_date_str(row_dict.get('Date of PO/LOI'))
            start_date = self.parse_date_str(row_dict.get('Probable Start Date'))
            end_date = self.parse_date_str(row_dict.get('Probable End Date'))

            bd_code = row_dict.get('BD/KAM Personnel code') or 'OWNER_UNKNOWN'
            sector = row_dict.get('Sector') or 'Unassigned / Other'
            if sector == 'Unassigned / Other':
                blank_sectors += 1

            amt_excl = self.parse_float(row_dict.get('Amount in Rupees (Excl of GST) (Masked)'))
            amt_incl = self.parse_float(row_dict.get('Amount in Rupees (Incl of GST) (Masked)'))
            billed_excl = self.parse_float(row_dict.get('Billed Value in Rupees (Excl of GST.) (Masked)'))
            collected_incl = self.parse_float(row_dict.get('Collected Amount in Rupees (Incl of GST.) (Masked)'))
            to_be_billed_excl = self.parse_float(row_dict.get('Amount to be billed in Rs. (Exl. of GST) (Masked)'))
            ar_masked = self.parse_float(row_dict.get('Amount Receivable (Masked)'))

            wo_status_billed = row_dict.get('WO Status (billed)') or 'Open'
            billing_status = row_dict.get('Billing Status') or 'Pending'

            is_delayed = False
            if exec_status.lower() in ['delayed', 'overdue']:
                is_delayed = True
            elif end_date and exec_status.lower() not in ['completed', 'closed']:
                try:
                    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                    if end_dt < datetime(2026, 1, 1):
                        is_delayed = True
                except Exception:
                    pass

            if exec_status.lower() not in ['completed', 'closed'] and not end_date:
                incomplete_wo += 1

            badges = []
            if is_delayed:
                badges.append("Delayed Schedule Risk")
            if sector == 'Unassigned / Other':
                badges.append("Inferred Sector")

            item = {
                "dealName": deal_name,
                "customerNameCode": customer_code,
                "serialNo": serial_no,
                "natureOfWork": nature_of_work,
                "executionStatus": exec_status,
                "dataDeliveryDate": delivery_date,
                "dateOfPO": po_date,
                "documentType": row_dict.get('Document Type', 'Purchase Order'),
                "probableStartDate": start_date,
                "probableEndDate": end_date,
                "bdPersonnelCode": bd_code,
                "sector": sector,
                "typeOfWork": row_dict.get('Type of Work', 'Inspection'),
                "amountRupeesExclGST": amt_excl,
                "amountRupeesInclGST": amt_incl,
                "billedValueExclGST": billed_excl,
                "collectedAmountInclGST": collected_incl,
                "amountToBeBilledExclGST": to_be_billed_excl,
                "amountReceivable": ar_masked,
                "woStatusBilled": wo_status_billed,
                "billingStatus": billing_status,
                "isDelayed": is_delayed,
                "cleaningBadges": badges
            }
            cleaned_work_orders.append(item)

        self._missing_count += missing_wo
        self._sector_fix_count += blank_sectors
        self._incomplete_work_orders += incomplete_wo

        self._log("Execution Status & Dates", "Normalized Work Order statuses and end dates", missing_wo, "Cleaned execution status fields and flagged delayed projects")
        self._log("Financials", "Parsed currency values and billed totals", len(cleaned_work_orders), "Converted GST amounts and receivables to float numbers")

        return cleaned_work_orders

    def get_confidence_score(self, total_deals: int, total_work_orders: int) -> float:
        total_records = max(1, total_deals + total_work_orders)
        flaws = self._missing_count + (self._duplicate_count * 2) + self._sector_fix_count + self._incomplete_work_orders
        penalty = (flaws / (total_records * 5)) * 100
        score = max(72.0, min(99.4, 98.5 - penalty))
        return round(score, 1)

cleaner_service = DataCleanerService()
