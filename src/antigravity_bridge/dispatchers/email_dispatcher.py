"""
Context-Aware Email Dispatch Engine for Antigravity Cloud Bridge.
Uses Resend REST API with dynamic sender identities and automatic HTML wrapping.
"""

import os
import sys
import json
import urllib.request
import urllib.error

DEFAULT_DOMAIN = os.environ.get("SENDER_DOMAIN", "yourdomain.com")
SENDER_MAP = {
    "ci": f"DevOps Pipelines <ci@{DEFAULT_DOMAIN}>",
    "deploy": f"Deployment Monitor <deploy@{DEFAULT_DOMAIN}>",
    "review": f"Pull Request Reviews <reviews@{DEFAULT_DOMAIN}>",
    "alert": f"System Alerts <alerts@{DEFAULT_DOMAIN}>",
    "task": f"Task Tracker <tasks@{DEFAULT_DOMAIN}>",
    "default": f"AI Assistant <assistant@{DEFAULT_DOMAIN}>"
}

class EmailDispatcher:
    def __init__(self, resend_api_key, default_recipient):
        self.resend_api_key = resend_api_key
        self.default_recipient = default_recipient

    def get_sender(self, subject_or_context):
        ctx_lower = subject_or_context.lower()
        for key, sender in SENDER_MAP.items():
            if key != "default" and key in ctx_lower:
                return sender
        return SENDER_MAP["default"]

    def send(self, subject, body_text_or_markdown, recipient=None, context_hint=None):
        if not self.resend_api_key:
            print("[EmailDispatcher] RESEND_API_KEY not configured. Skipping email.", file=sys.stderr)
            return False

        target_recipient = recipient or self.default_recipient
        sender = self.get_sender(context_hint or subject)

        # Convert simple line breaks to HTML paragraphs
        html_paras = "".join(f"<p>{p.strip()}</p>" for p in body_text_or_markdown.split("\n\n") if p.strip())
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #1e293b; line-height: 1.6; max-width: 650px; margin: 20px auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
          <div style="background: #0f172a; color: white; padding: 12px 18px; border-radius: 6px; font-weight: bold; margin-bottom: 18px;">
            Antigravity Cloud Bridge &bull; Notification
          </div>
          <h2 style="color: #0f172a; font-size: 18px; border-bottom: 2px solid #3b82f6; padding-bottom: 8px;">{subject}</h2>
          <div style="font-size: 14px; color: #334155;">
            {html_paras}
          </div>
          <div style="margin-top: 30px; padding-top: 12px; border-top: 1px solid #e2e8f0; font-size: 12px; color: #94a3b8;">
            Sent autonomously via Antigravity Cloud Bridge &bull; Resend Engine
          </div>
        </body>
        </html>
        """

        payload = {
            "from": sender,
            "to": [target_recipient],
            "subject": subject,
            "html": html_content,
            "text": body_text_or_markdown
        }

        url = "https://api.resend.com/emails"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.resend_api_key}",
                "Content-Type": "application/json",
                "User-Agent": "Antigravity-Bridge/1.0"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                print(f"[EmailDispatcher] SUCCESS: Dispatched email '{subject}' to {target_recipient} [ID: {data.get('id')}]")
                return True
        except Exception as e:
            print(f"[EmailDispatcher] Failed to send email: {e}", file=sys.stderr)
            return False

def send_email_notification(subject, body, context_hint=None):
    from ..core.config import load_config
    cfg = load_config()
    disp = EmailDispatcher(cfg["RESEND_API_KEY"], cfg["NOTIFICATION_EMAIL"])
    return disp.send(subject, body, context_hint=context_hint)
