"""
Telegram Dispatcher and Client Engine for Antigravity Cloud Bridge.
Supports text chunking (4096-char ceiling), multipart binary upload, and message deletion.
"""

import os
import sys
import json
import urllib.request
import urllib.parse
import urllib.error

class TelegramDispatcher:
    def __init__(self, token, default_chat_id=None, email_fallback_fn=None):
        self.token = token
        self.default_chat_id = str(default_chat_id) if default_chat_id else None
        self.email_fallback_fn = email_fallback_fn

    def api_call(self, method, params=None):
        url = f"https://api.telegram.org/bot{self.token}/{method}"
        headers = {"User-Agent": "Antigravity-Bridge/1.0"}
        
        if params:
            data = json.dumps(params).encode("utf-8")
            headers["Content-Type"] = "application/json"
            req = urllib.request.Request(url, data=data, headers=headers)
        else:
            req = urllib.request.Request(url, headers=headers)
            
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def send_text(self, text, chat_id=None, parse_mode="Markdown"):
        target_chat_id = str(chat_id or self.default_chat_id)
        if not target_chat_id:
            raise ValueError("No target chat_id provided for send_text.")

        # Chunk messages at 3800 chars to avoid 4096-char Telegram ceiling
        max_len = 3800
        chunks = [text[i:i + max_len] for i in range(0, len(text), max_len)] if len(text) > max_len else [text]
        
        try:
            for chunk in chunks:
                try:
                    self.api_call("sendMessage", {
                        "chat_id": target_chat_id,
                        "text": chunk,
                        "parse_mode": parse_mode
                    })
                except Exception:
                    # Fallback to plain text if Markdown parsing errors out
                    self.api_call("sendMessage", {
                        "chat_id": target_chat_id,
                        "text": chunk
                    })
            return True
        except Exception as e:
            print(f"[TelegramDispatcher] Text dispatch failed: {e}", file=sys.stderr)
            if self.email_fallback_fn:
                print("[TelegramDispatcher] Triggering Email Fallback...", file=sys.stderr)
                self.email_fallback_fn("Telegram Delivery Fallback: " + text[:50], text)
            return False

    def send_document(self, file_path, caption="", chat_id=None):
        target_chat_id = str(chat_id or self.default_chat_id)
        if not target_chat_id:
            raise ValueError("No target chat_id provided for send_document.")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        boundary = "----AntigravityMultipartBoundaryXYZ987"
        lines = [
            f"--{boundary}",
            'Content-Disposition: form-data; name="chat_id"',
            "",
            target_chat_id
        ]
        if caption:
            lines.extend([
                f"--{boundary}",
                'Content-Disposition: form-data; name="caption"',
                "",
                caption
            ])

        filename = os.path.basename(file_path)
        lines.extend([
            f"--{boundary}",
            f'Content-Disposition: form-data; name="document"; filename="{filename}"',
            "Content-Type: application/octet-stream",
            ""
        ])

        header_bytes = "\r\n".join(lines).encode("utf-8") + b"\r\n"
        footer_bytes = f"\r\n--{boundary}--\r\n".encode("utf-8")

        with open(file_path, "rb") as f:
            file_bytes = f.read()

        body = header_bytes + file_bytes + footer_bytes
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{self.token}/sendDocument",
            data=body,
            headers={
                "Content-Type": f"multipart/form-data; boundary={boundary}",
                "User-Agent": "Antigravity-Bridge/1.0"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                return res
        except Exception as e:
            print(f"[TelegramDispatcher] Document dispatch failed: {e}", file=sys.stderr)
            if self.email_fallback_fn:
                self.email_fallback_fn(f"File Delivery Fallback: {filename}", f"File could not be sent to Telegram: {filename}\nCaption: {caption}")
            return None

    def delete_message(self, message_id, chat_id=None):
        target_chat_id = str(chat_id or self.default_chat_id)
        try:
            return self.api_call("deleteMessage", {
                "chat_id": target_chat_id,
                "message_id": message_id
            })
        except Exception as e:
            print(f"[TelegramDispatcher] deleteMessage {message_id} failed: {e}", file=sys.stderr)
            return None

def send_telegram_text(text, chat_id=None):
    from ..core.config import load_config
    cfg = load_config()
    disp = TelegramDispatcher(cfg["TELEGRAM_BOT_TOKEN"], cfg["TELEGRAM_CHAT_ID"])
    return disp.send_text(text, chat_id)

def send_telegram_file(file_path, caption="", chat_id=None):
    from ..core.config import load_config
    cfg = load_config()
    disp = TelegramDispatcher(cfg["TELEGRAM_BOT_TOKEN"], cfg["TELEGRAM_CHAT_ID"])
    return disp.send_document(file_path, caption, chat_id)

def delete_telegram_message(message_id, chat_id=None):
    from ..core.config import load_config
    cfg = load_config()
    disp = TelegramDispatcher(cfg["TELEGRAM_BOT_TOKEN"], cfg["TELEGRAM_CHAT_ID"])
    return disp.delete_message(message_id, chat_id)
