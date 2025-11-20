from __future__ import annotations
import os, json, requests

def send_telegram(text: str) -> dict:
    token = os.getenv("TRADERCOPILOT_BOT_TOKEN","").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID","").strip()
    if not token or not chat_id:
        return {"ok": False, "error": "Missing bot token or chat id in env"}
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    try:
        r = requests.post(url, json=payload, timeout=8)
        ok = r.status_code == 200
        return {"ok": ok, "status": r.status_code, "data": r.json() if ok else r.text}
    except Exception as e:
        return {"ok": False, "error": str(e)}
