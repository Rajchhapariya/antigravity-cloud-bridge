"""
Idempotent Ledger and State Persistence Engine for Antigravity Cloud Bridge.
Prevents duplicate ingestion, tracks execution status, and logs structured mobile items.
"""

import os
import json
from datetime import datetime

class LedgerManager:
    def __init__(self, ledger_file, offset_file):
        self.ledger_file = ledger_file
        self.offset_file = offset_file
        os.makedirs(os.path.dirname(self.ledger_file), exist_ok=True)
        os.makedirs(os.path.dirname(self.offset_file), exist_ok=True)

    def load_ledger(self):
        if os.path.exists(self.ledger_file):
            try:
                with open(self.ledger_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {"items": []}
        return {"items": []}

    def save_ledger(self, ledger_data):
        with open(self.ledger_file, "w", encoding="utf-8") as f:
            json.dump(ledger_data, f, indent=2)

    def record_item(self, update_id, telegram_ts, file_path, item_type, caption="", is_trigger=False, clean_cmd=""):
        ledger = self.load_ledger()
        
        for entry in ledger.get("items", []):
            if entry.get("update_id") == update_id:
                return entry

        entry = {
            "update_id": update_id,
            "item_type": item_type,
            "filename": os.path.basename(file_path) if file_path else None,
            "file_path": file_path,
            "caption": caption,
            "urgency": "IMMEDIATE" if is_trigger else "BUFFERED",
            "instruction": clean_cmd if is_trigger else caption,
            "telegram_timestamp": datetime.fromtimestamp(telegram_ts).isoformat(),
            "synced_at": datetime.now().isoformat(),
            "status": "new"
        }
        ledger.setdefault("items", []).append(entry)
        self.save_ledger(ledger)
        return entry

    def update_item_status(self, update_id, new_status, summary=""):
        ledger = self.load_ledger()
        for item in ledger.get("items", []):
            if item.get("update_id") == update_id:
                item["status"] = new_status
                item["actioned_at"] = datetime.now().isoformat()
                if summary:
                    item["summary"] = summary
                break
        self.save_ledger(ledger)

    def get_last_offset(self):
        if os.path.exists(self.offset_file):
            try:
                with open(self.offset_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("offset", 0)
            except Exception:
                return 0
        return 0

    def save_last_offset(self, offset):
        with open(self.offset_file, "w", encoding="utf-8") as f:
            json.dump({"offset": offset, "updated_at": datetime.now().isoformat()}, f)
