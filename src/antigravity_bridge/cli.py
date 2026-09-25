"""
Command Line Interface for Antigravity Cloud Bridge.
"""

import sys
import argparse
from .core.config import load_config
from .core.daemon import run_daemon, sync_once
from .dispatchers.telegram_dispatcher import send_telegram_text, send_telegram_file
from .dispatchers.email_dispatcher import send_email_notification
from .sanitizers.media_sanitizer import sanitize_signature, sanitize_photo, sanitize_pdf

def main():
    parser = argparse.ArgumentParser(
        prog="antigravity-bridge",
        description="Autonomous Two-Way Telegram & Resend Bridge for Agentic AI Coding Assistants"
    )
    
    parser.add_argument("--daemon", action="store_true", help="Run continuously in background polling loop")
    parser.add_argument("--interval", type=int, default=3, help="Polling interval in seconds (default: 3)")
    parser.add_argument("--sync", action="store_true", help="Perform a single-shot synchronization and exit")
    parser.add_argument("--send-text", type=str, help="Send a text message directly to Telegram")
    parser.add_argument("--send-file", type=str, help="Send a document or image file directly to Telegram")
    parser.add_argument("--caption", type=str, default="", help="Optional caption when sending a file")
    parser.add_argument("--send-email", nargs=2, metavar=("SUBJECT", "BODY"), help="Send an email notification via Resend")
    parser.add_argument("--sanitize-sig", type=str, help="Sanitize a signature image (#FFFFFF background, cropped, <100KB)")
    parser.add_argument("--sanitize-photo", type=str, help="Sanitize a passport photo (centered crop, <200KB)")
    parser.add_argument("--sanitize-pdf", type=str, help="Compress a PDF to strictly under 1MB")

    args = parser.parse_args()

    cfg = load_config()

    if args.daemon:
        run_daemon(cfg, interval=args.interval)
    elif args.sync:
        count, items = sync_once(cfg)
        print(f"Synced {count} pending items: {items}")
    elif args.send_text:
        send_telegram_text(args.send_text)
    elif args.send_file:
        send_telegram_file(args.send_file, caption=args.caption)
    elif args.send_email:
        send_email_notification(args.send_email[0], args.send_email[1])
    elif args.sanitize_sig:
        out = sanitize_signature(args.sanitize_sig)
        print(f"Sanitized signature: {out}")
    elif args.sanitize_photo:
        out = sanitize_photo(args.sanitize_photo)
        print(f"Sanitized photo: {out}")
    elif args.sanitize_pdf:
        out = sanitize_pdf(args.sanitize_pdf)
        print(f"Sanitized PDF: {out}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
