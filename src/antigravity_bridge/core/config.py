"""
Configuration Manager for Antigravity Cloud Bridge.
Loads environment variables from OS or standard .env files.
"""

import os
import sys
from pathlib import Path

def load_config():
    # Attempt loading dotenv if installed from local directory
    try:
        from dotenv import load_dotenv
        load_dotenv()
        local_env = Path("./.env.local")
        if local_env.exists():
            load_dotenv(local_env)
    except ImportError:
        pass

    config = {
        "TELEGRAM_BOT_TOKEN": os.environ.get("TELEGRAM_BOT_TOKEN"),
        "TELEGRAM_CHAT_ID": os.environ.get("TELEGRAM_CHAT_ID"),
        "RESEND_API_KEY": os.environ.get("RESEND_API_KEY"),
        "NOTIFICATION_EMAIL": os.environ.get("NOTIFICATION_EMAIL_RECIPIENT", ""),
        "SENDER_EMAIL": os.environ.get("SENDER_DEFAULT_IDENTITY", "AI Assistant <noreply@yourdomain.com>"),
        "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY"),
        "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY"),
        "OPENROUTER_API_KEY": os.environ.get("OPENROUTER_API_KEY"),
        "SYSTEM_INSTRUCTION": os.environ.get("SYSTEM_INSTRUCTION"),
        "INBOX_DIR": os.environ.get("INBOX_DIR", os.path.abspath("./inbox")),
        "LEDGER_FILE": os.environ.get("LEDGER_FILE", os.path.abspath("./inbox/inbox_ledger.json")),
        "OFFSET_FILE": os.environ.get("OFFSET_FILE", os.path.abspath("./inbox/.telegram_offset.json")),
        "NOTES_FILE": os.environ.get("NOTES_FILE", os.path.abspath("./inbox/mobile_notes.md")),
        "POLL_INTERVAL": int(os.environ.get("POLL_INTERVAL", 3)),
    }

    return config
