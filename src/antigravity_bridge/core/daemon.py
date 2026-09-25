"""
Core Ingestion Daemon & Synchronization Engine for Antigravity Cloud Bridge.
Polls Telegram Bot API, stores incoming items, runs triggers, and dispatches responses.
"""

import os
import sys
import json
import time
from datetime import datetime

from .config import load_config
from .ledger import LedgerManager
from .ai_resolver import AIResolver
from ..dispatchers.telegram_dispatcher import TelegramDispatcher
from ..dispatchers.email_dispatcher import EmailDispatcher
from ..sanitizers.media_sanitizer import sanitize_signature, sanitize_photo, sanitize_pdf
from ..generators.office_generator import create_docx, create_pptx, create_xlsx, create_pdf, create_standalone_app

def parse_trigger(raw_text):
    if not raw_text:
        return False, ""
    cleaned = raw_text.strip()
    trigger_patterns = ["- now", "-now", "--now", "- NOW", "-Now"]
    for p in trigger_patterns:
        if p in cleaned:
            clean_cmd = cleaned.replace(p, "").strip()
            return True, clean_cmd
    return False, cleaned

def handle_autonomous_doc(clean_cmd, ai_resolver, telegram_dispatcher, base_dir):
    cmd_lower = clean_cmd.lower()

    # 1. Word / Docx
    if any(k in cmd_lower for k in ["dock", "docx", "word doc", "word file", "create doc", "doc file", "a doc"]):
        prompt = (
            f"Generate a professional document outline for: '{clean_cmd}'. "
            "Output valid JSON ONLY with schema: {\"title\": \"...\", \"sections\": [{\"heading\": \"...\", \"content\": [\"bullet 1\", \"bullet 2\"]}]}"
        )
        ai_resp = ai_resolver.ask(prompt)
        title = clean_cmd[:30]
        sections = [{"heading": "Overview", "content": clean_cmd}]
        try:
            start_idx = ai_resp.find("{")
            end_idx = ai_resp.rfind("}") + 1
            if start_idx != -1 and end_idx > start_idx:
                data = json.loads(ai_resp[start_idx:end_idx])
                title = data.get("title", title)
                sections = data.get("sections", sections)
        except Exception:
            pass
        out_f = create_docx(title, sections, base_dir=base_dir)
        telegram_dispatcher.send_document(out_f, caption=f"Generated Word Document: {title}")
        return True, f"Word Doc: {title}"

    # 2. PDF Document
    elif any(k in cmd_lower for k in ["pdf", "apdf", "create pdf", "make a pdf", "generate pdf"]):
        prompt = (
            f"Generate a structured formal PDF report outline for: '{clean_cmd}'. "
            "Output valid JSON ONLY with schema: {\"title\": \"...\", \"sections\": [{\"heading\": \"...\", \"content\": [\"bullet 1\", \"bullet 2\"]}]}"
        )
        ai_resp = ai_resolver.ask(prompt)
        title = clean_cmd[:30]
        sections = [{"heading": "Executive Summary", "content": clean_cmd}]
        try:
            start_idx = ai_resp.find("{")
            end_idx = ai_resp.rfind("}") + 1
            if start_idx != -1 and end_idx > start_idx:
                data = json.loads(ai_resp[start_idx:end_idx])
                title = data.get("title", title)
                sections = data.get("sections", sections)
        except Exception:
            pass
        out_f = create_pdf(title, sections, base_dir=base_dir)
        telegram_dispatcher.send_document(out_f, caption=f"Generated PDF Document: {title}")
        return True, f"PDF: {title}"

    # 3. PowerPoint / PPTX
    elif any(k in cmd_lower for k in ["ppt", "pptx", "presentation", "slides"]):
        prompt = (
            f"Generate professional presentation slides for: '{clean_cmd}'. "
            "Output valid JSON ONLY with schema: {\"title\": \"...\", \"subtitle\": \"...\", \"slides\": [{\"title\": \"...\", \"bullets\": [\"pt 1\", \"pt 2\"]}]}"
        )
        ai_resp = ai_resolver.ask(prompt)
        title = clean_cmd[:30]
        subtitle = ""
        slides = [{"title": "Overview", "bullets": [clean_cmd]}]
        try:
            start_idx = ai_resp.find("{")
            end_idx = ai_resp.rfind("}") + 1
            if start_idx != -1 and end_idx > start_idx:
                data = json.loads(ai_resp[start_idx:end_idx])
                title = data.get("title", title)
                subtitle = data.get("subtitle", "")
                slides = data.get("slides", slides)
        except Exception:
            pass
        out_f = create_pptx(title, subtitle, slides, base_dir=base_dir)
        telegram_dispatcher.send_document(out_f, caption=f"Generated PowerPoint: {title}")
        return True, f"PowerPoint: {title}"

    # 4. Excel / XLSX
    elif any(k in cmd_lower for k in ["excel", "xlsx", "spreadsheet", "sheet"]):
        prompt = (
            f"Generate tabular spreadsheet data for: '{clean_cmd}'. "
            "Output valid JSON ONLY with schema: {\"title\": \"...\", \"headers\": [\"Col1\", \"Col2\"], \"rows\": [[\"val1\", \"val2\"]] }"
        )
        ai_resp = ai_resolver.ask(prompt)
        title = clean_cmd[:30]
        headers = ["Item", "Details"]
        rows = [[clean_cmd, "Processed"]]
        try:
            start_idx = ai_resp.find("{")
            end_idx = ai_resp.rfind("}") + 1
            if start_idx != -1 and end_idx > start_idx:
                data = json.loads(ai_resp[start_idx:end_idx])
                title = data.get("title", title)
                headers = data.get("headers", headers)
                rows = data.get("rows", rows)
        except Exception:
            pass
        out_f = create_xlsx(title, headers, rows, base_dir=base_dir)
        telegram_dispatcher.send_document(out_f, caption=f"Generated Spreadsheet: {title}")
        return True, f"Excel: {title}"

    # 5. Standalone Web App
    elif any(k in cmd_lower for k in ["create app", "create an app", "web app", "build an app", "build app", "make an app"]):
        prompt = (
            f"Build a complete single-file HTML/CSS/JS progressive web application for: '{clean_cmd}'. "
            "Ensure modern UI, responsive touch layout, zero external dependencies, and complete interactivity. "
            "Output ONLY raw HTML starting with <!DOCTYPE html> and ending with </html> without markdown backticks."
        )
        app_code = ai_resolver.ask(prompt)
        if app_code.startswith("```html"):
            app_code = app_code[7:]
        if app_code.startswith("```"):
            app_code = app_code[3:]
        if app_code.endswith("```"):
            app_code = app_code[:-3]
        app_code = app_code.strip()
        
        title = clean_cmd.replace("create app", "").replace("build app", "").strip()[:25] or "Standalone_App"
        out_f = create_standalone_app(title, app_code, base_dir=base_dir)
        telegram_dispatcher.send_document(out_f, caption=f"Generated Web App: {title} (Open in any browser)")
        return True, f"Web App: {title}"

    return False, None

def download_telegram_file(token, file_id, dest_path):
    import urllib.request
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    url_info = f"https://api.telegram.org/bot{token}/getFile?file_id={file_id}"
    req = urllib.request.Request(url_info, headers={"User-Agent": "Antigravity-Bridge/1.0"})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    file_rel_path = data.get("result", {}).get("file_path")
    if not file_rel_path:
        raise ValueError(f"Could not retrieve file_path for file_id: {file_id}")
    
    download_url = f"https://api.telegram.org/file/bot{token}/{file_rel_path}"
    req2 = urllib.request.Request(download_url, headers={"User-Agent": "Antigravity-Bridge/1.0"})
    with urllib.request.urlopen(req2) as resp, open(dest_path, "wb") as out_f:
        out_f.write(resp.read())
    return dest_path

def sync_once(config=None):
    cfg = config or load_config()
    token = cfg["TELEGRAM_BOT_TOKEN"]
    chat_id = cfg["TELEGRAM_CHAT_ID"]
    inbox_dir = cfg["INBOX_DIR"]
    os.makedirs(inbox_dir, exist_ok=True)

    ledger_mgr = LedgerManager(cfg["LEDGER_FILE"], cfg["OFFSET_FILE"])
    ai_resolver = AIResolver(cfg)
    
    email_disp = EmailDispatcher(cfg["RESEND_API_KEY"], cfg["NOTIFICATION_EMAIL"])
    tele_disp = TelegramDispatcher(token, chat_id, email_fallback_fn=email_disp.send)

    offset = ledger_mgr.get_last_offset()
    params = {"timeout": 5}
    if offset > 0:
        params["offset"] = offset

    data = tele_disp.api_call("getUpdates", params)
    updates = data.get("result", [])
    if not updates:
        return 0, []

    processed = []
    max_update_id = offset - 1

    for update in updates:
        up_id = update["update_id"]
        if up_id > max_update_id:
            max_update_id = up_id

        msg = update.get("message") or update.get("channel_post")
        if not msg:
            continue

        sender_id = str(msg.get("chat", {}).get("id"))
        if chat_id and sender_id != str(chat_id):
            continue

        ts_str = datetime.fromtimestamp(msg.get("date", time.time())).strftime("%Y%m%d_%H%M%S")
        caption = msg.get("caption", "").strip()

        # 1. Document
        if "document" in msg:
            doc = msg["document"]
            orig_name = doc.get("file_name", f"doc_{ts_str}.bin")
            save_path = os.path.join(inbox_dir, orig_name)
            if os.path.exists(save_path):
                b, e = os.path.splitext(orig_name)
                save_path = os.path.join(inbox_dir, f"{b}_{ts_str}{e}")
            download_telegram_file(token, doc["file_id"], save_path)
            
            # Rule 1 auto-compression if PDF > 1MB
            if save_path.lower().endswith(".pdf") and os.path.getsize(save_path) > 1048576:
                save_path = sanitize_pdf(save_path)

            is_trig, clean_cmd = parse_trigger(caption)
            ledger_mgr.record_item(up_id, msg.get("date", time.time()), save_path, "document", caption, is_trig, clean_cmd)
            processed.append(f"Document: {os.path.basename(save_path)}")

            if is_trig:
                tele_disp.send_text(f"IMMEDIATE TRIGGER ACKNOWLEDGED: '{clean_cmd or os.path.basename(save_path)}'. Processing now.")
                reply = ai_resolver.ask(clean_cmd or f"Analyze: {os.path.basename(save_path)}")
                tele_disp.send_text(reply)
            else:
                tele_disp.send_text(f"Buffered to Antigravity Inbox: `{os.path.basename(save_path)}`.")

        # 2. Photo
        elif "photo" in msg:
            photo = msg["photo"][-1]
            save_path = os.path.join(inbox_dir, f"screenshot_{ts_str}_{photo['file_id'][:6]}.jpg")
            download_telegram_file(token, photo["file_id"], save_path)
            is_trig, clean_cmd = parse_trigger(caption)
            ledger_mgr.record_item(up_id, msg.get("date", time.time()), save_path, "photo", caption, is_trig, clean_cmd)
            processed.append(f"Photo: {os.path.basename(save_path)}")

            if is_trig:
                tele_disp.send_text(f"IMMEDIATE TRIGGER ACKNOWLEDGED: '{clean_cmd or os.path.basename(save_path)}'. Processing now.")
                cmd_low = clean_cmd.lower()
                if "signature" in cmd_low or ("sanitize" in cmd_low and "photo" not in cmd_low):
                    san = sanitize_signature(save_path)
                    tele_disp.send_document(san, caption="Sanitized Signature (#FFFFFF, cropped, <100KB)")
                elif "photo" in cmd_low or "passport" in cmd_low:
                    san = sanitize_photo(save_path)
                    tele_disp.send_document(san, caption="Sanitized Passport Photo (centered, <200KB)")
                reply = ai_resolver.ask(clean_cmd or "Analyze this image.", image_path=save_path)
                tele_disp.send_text(reply)
            else:
                tele_disp.send_text(f"Buffered to Antigravity Inbox: `{os.path.basename(save_path)}`.")

        # 3. Voice
        elif "voice" in msg:
            save_path = os.path.join(inbox_dir, f"voice_{ts_str}.oga")
            download_telegram_file(token, msg["voice"]["file_id"], save_path)
            is_trig, clean_cmd = parse_trigger(caption)
            ledger_mgr.record_item(up_id, msg.get("date", time.time()), save_path, "voice", caption, is_trig, clean_cmd)
            processed.append(f"Voice Note: {os.path.basename(save_path)}")
            if is_trig:
                tele_disp.send_text(f"IMMEDIATE TRIGGER ACKNOWLEDGED for Voice Note. Processing now.")
            else:
                tele_disp.send_text(f"Buffered voice note to Inbox: `{os.path.basename(save_path)}`.")

        # 4. Text
        elif "text" in msg:
            raw_text = msg["text"].strip()
            is_trig, clean_cmd = parse_trigger(raw_text)
            notes_file = cfg["NOTES_FILE"]
            with open(notes_file, "a", encoding="utf-8") as f:
                f.write(f"\n### [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] (Urgency: {'IMMEDIATE' if is_trig else 'BUFFERED'})\n{raw_text}\n")
            ledger_mgr.record_item(up_id, msg.get("date", time.time()), notes_file, "text", raw_text, is_trig, clean_cmd)
            processed.append(f"Text: {clean_cmd[:50]}...")

            if is_trig:
                tele_disp.send_text(f"IMMEDIATE TRIGGER ACKNOWLEDGED: '{clean_cmd}'. Processing now.")
                handled, summary = handle_autonomous_doc(clean_cmd, ai_resolver, tele_disp, inbox_dir)
                if not handled:
                    reply = ai_resolver.ask(clean_cmd)
                    tele_disp.send_text(reply)
            else:
                tele_disp.send_text("Note buffered to Antigravity Inbox.")

    ledger_mgr.save_last_offset(max_update_id + 1)
    return len(processed), processed

def run_daemon(config=None, interval=None):
    cfg = config or load_config()
    poll_int = interval or cfg["POLL_INTERVAL"]
    print(f"Starting Antigravity Cloud Bridge Daemon (polling every {poll_int}s)...")
    while True:
        try:
            count, items = sync_once(cfg)
            if count > 0:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Ingested {count} items: {items}")
        except Exception as e:
            print(f"Error in sync loop: {e}", file=sys.stderr)
        time.sleep(poll_int)
