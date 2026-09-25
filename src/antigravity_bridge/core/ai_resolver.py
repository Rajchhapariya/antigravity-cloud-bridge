"""
Multi-Engine Autonomous LLM Resolver with Multi-Provider Fallbacks.
Primary: OpenAI (gpt-4o-mini) -> Secondary: Google Gemini -> Tertiary: OpenRouter.
"""

import os
import sys
import json
import base64
import urllib.request
from datetime import datetime

class AIResolver:
    def __init__(self, config):
        self.config = config

    def ask(self, prompt, image_path=None, system_override=None):
        now_str = datetime.now().strftime("%A, %d %B %Y, %I:%M:%S %p")
        config_inst = self.config.get("SYSTEM_INSTRUCTION")
        default_system = (
            f"Current local time and date: {now_str}. "
            "You are an autonomous AI software engineering and development assistant. "
            "Strictly ZERO emojis in all responses. "
            "Write with direct, punchy, concise, technically confident, non-AI human cadence."
        )
        system_inst = system_override or config_inst or default_system

        # 1. High-Speed Direct OpenAI Engine (gpt-4o-mini)
        openai_key = self.config.get("OPENAI_API_KEY")
        if openai_key:
            try:
                url = "https://api.openai.com/v1/chat/completions"
                messages = [
                    {"role": "system", "content": system_inst},
                    {"role": "user", "content": prompt}
                ]
                payload = {
                    "model": "gpt-4o-mini",
                    "messages": messages,
                    "temperature": 0.4
                }
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=12) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    return data["choices"][0]["message"]["content"].strip()
            except Exception as e:
                print(f"[AIResolver] OpenAI provider failed: {e}", file=sys.stderr)

        # 2. Google Gemini REST Engine
        gemini_key = self.config.get("GEMINI_API_KEY")
        if gemini_key:
            for m in ["models/gemini-3.8-flash", "models/gemini-flash-latest", "models/gemini-2.5-flash"]:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/{m}:generateContent?key={gemini_key}"
                    parts = [{"text": f"{system_inst}\n\nUser: {prompt}"}]
                    if image_path and os.path.exists(image_path):
                        with open(image_path, "rb") as img_f:
                            b64_img = base64.b64encode(img_f.read()).decode("utf-8")
                        parts.append({
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": b64_img
                            }
                        })
                    payload = {"contents": [{"parts": parts}]}
                    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
                    with urllib.request.urlopen(req, timeout=12) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
                except Exception:
                    continue

        # 3. OpenRouter Free Fallback
        openrouter_key = self.config.get("OPENROUTER_API_KEY")
        if openrouter_key:
            try:
                url = "https://openrouter.ai/api/v1/chat/completions"
                payload = {
                    "model": "google/gemini-2.0-flash-exp:free",
                    "messages": [
                        {"role": "system", "content": system_inst},
                        {"role": "user", "content": prompt}
                    ]
                }
                req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Authorization": f"Bearer {openrouter_key}", "Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    return data["choices"][0]["message"]["content"].strip()
            except Exception as e:
                print(f"[AIResolver] OpenRouter fallback failed: {e}", file=sys.stderr)

        return "Antigravity received your request, but AI generation was temporarily unavailable."
