import csv
import json
import os
import urllib.request
import ssl
from typing import Dict, List, Any, Tuple
from app.config import settings
from app.services.cleaner_service import cleaner_service

class MondayService:
    def __init__(self):
        self.api_url = settings.MONDAY_API_URL
        self.ssl_ctx = ssl._create_unverified_context()

    def query_monday_api(self, api_token: str, board_id: str) -> List[Dict[str, Any]]:
        if not api_token or not board_id:
            return []

        headers = {
            "Authorization": api_token,
            "Content-Type": "application/json",
            "API-Version": "2023-10",
            "User-Agent": "Mozilla/5.0"
        }

        query = """
        query ($board_id: [ID!]) {
          boards (ids: $board_id) {
            name
            items_page {
              items {
                id
                name
                column_values {
                  id
                  text
                  value
                }
              }
            }
          }
        }
        """
        payload = json.dumps({"query": query, "variables": {"board_id": [board_id]}}).encode('utf-8')

        try:
            req = urllib.request.Request(self.api_url, data=payload, headers=headers, method='POST')
            with urllib.request.urlopen(req, context=self.ssl_ctx, timeout=10) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode('utf-8'))
                    boards = data.get("data", {}).get("boards", [])
                    if boards and len(boards) > 0:
                        items = boards[0].get("items_page", {}).get("items", [])
                        raw_rows = []
                        for item in items:
                            row = {"Deal Name": item.get("name", "")}
                            for col in item.get("column_values", []):
                                row[col.get("id")] = col.get("text", "")
                            raw_rows.append(row)
                        return raw_rows
        except Exception as e:
            print(f"Error calling Monday API: {e}")
        return []

    def verify_connection(self, api_token: str, deal_board_id: str, work_board_id: str) -> Tuple[bool, str, Dict[str, Any]]:
        headers = {
            "Authorization": api_token,
            "Content-Type": "application/json",
            "API-Version": "2023-10",
            "User-Agent": "Mozilla/5.0"
        }
        query = """
        query ($board_ids: [ID!]) {
          boards (ids: $board_ids) {
            id
            name
            items_page {
              items {
                id
              }
            }
          }
        }
        """
        payload = json.dumps({"query": query, "variables": {"board_ids": [deal_board_id, work_board_id]}}).encode('utf-8')

        try:
            req = urllib.request.Request(self.api_url, data=payload, headers=headers, method='POST')
            with urllib.request.urlopen(req, context=self.ssl_ctx, timeout=10) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode('utf-8'))
                    if "errors" in data:
                        return False, f"Monday API Error: {data['errors'][0].get('message')}", {}
                    boards = data.get("data", {}).get("boards", [])
                    if len(boards) >= 1:
                        deal_board = boards[0]
                        work_board = boards[1] if len(boards) > 1 else boards[0]
                        return True, "Successfully connected to Monday.com boards!", {
                            "dealBoardName": deal_board.get("name"),
                            "workBoardName": work_board.get("name"),
                            "dealItemsCount": len(deal_board.get("items_page", {}).get("items", [])),
                            "workItemsCount": len(work_board.get("items_page", {}).get("items", []))
                        }
                    return False, "No boards found matching the provided IDs.", {}
                else:
                    return False, f"HTTP Error {resp.status}", {}
        except Exception as e:
            return False, f"Network connection failed: {str(e)}", {}

    def fetch_deals_data(self, api_token: str = "", board_id: str = "") -> List[Dict[str, Any]]:
        if api_token and board_id:
            api_rows = self.query_monday_api(api_token, board_id)
            if api_rows:
                return cleaner_service.clean_deals_data(api_rows)

        csv_path = settings.DEAL_FUNNEL_CSV
        raw_rows = []
        if os.path.exists(csv_path):
            with open(csv_path, mode='r', encoding='utf-8-sig', errors='replace') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    raw_rows.append(row)
        return cleaner_service.clean_deals_data(raw_rows)

    def fetch_work_orders_data(self, api_token: str = "", board_id: str = "") -> List[Dict[str, Any]]:
        if api_token and board_id:
            api_rows = self.query_monday_api(api_token, board_id)
            if api_rows:
                mapped_rows = []
                for r in api_rows:
                    mapped_rows.append([r.get(k, '') for k in r.keys()])
                return cleaner_service.clean_work_orders_data(mapped_rows)

        csv_path = settings.WORK_ORDER_CSV
        raw_lines = []
        if os.path.exists(csv_path):
            with open(csv_path, mode='r', encoding='utf-8-sig', errors='replace') as f:
                reader = csv.reader(f)
                for line in reader:
                    raw_lines.append(line)
        return cleaner_service.clean_work_orders_data(raw_lines)

monday_service = MondayService()
