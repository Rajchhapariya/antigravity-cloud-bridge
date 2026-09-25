"""
Antigravity Cloud Bridge: Autonomous Two-Way Telegram & Resend Bridge for Agentic AI Coding Assistants.
"""

__version__ = "1.0.0"
__author__ = "Raj Chhapariya"

from .core.config import load_config
from .core.daemon import run_daemon, sync_once
from .dispatchers.telegram_dispatcher import send_telegram_text, send_telegram_file, delete_telegram_message
from .dispatchers.email_dispatcher import send_email_notification
from .sanitizers.media_sanitizer import sanitize_signature, sanitize_photo, sanitize_pdf
from .generators.office_generator import create_docx, create_pptx, create_xlsx, create_pdf, create_standalone_app
