import os
import logging
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("styleflow-bot")

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
MINI_APP_URL = os.getenv("MINI_APP_URL", "").strip()
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "").strip().rstrip("/")
PORT = int(os.getenv("PORT", "5000"))

app = Flask(__name__)


def telegram_api(method: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Send request to Telegram Bot API."""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is missing")
        return None

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    try:
        response = requests.post(url, json=payload, timeout=10)
        try:
            data = response.json()
        except ValueError:
            data = {"ok": False, "description": response.text}

        if not response.ok or not data.get("ok"):
            logger.error("Telegram API error: %s", data)
        return data
    except requests.RequestException as exc:
        logger.exception("Telegram API request failed: %s", exc)
        return None


def send_start_message(chat_id: int) -> None:
    """Send /start message with Telegram Mini App button."""
    if not MINI_APP_URL:
        text = (
            "Assalomu alaykum! StyleFlow bot ishlayapti, lekin MINI_APP_URL sozlanmagan.\n\n"
            "Railway Variables ichiga MINI_APP_URL qo‘shing. Masalan:\n"
            "MINI_APP_URL=https://username.github.io/styleflow-frontend/client.html"
        )
        telegram_api("sendMessage", {"chat_id": chat_id, "text": text})
        return

    payload = {
        "chat_id": chat_id,
        "text": "Assalomu alaykum! StyleFlow ga xush kelibsiz. Barber booking appni ochish uchun tugmani bosing.",
        "reply_markup": {
            "inline_keyboard": [
                [
                    {
                        "text": "Open StyleFlow",
                        "web_app": {"url": MINI_APP_URL},
                    }
                ]
            ]
        },
    }
    telegram_api("sendMessage", payload)


def send_help_message(chat_id: int) -> None:
    payload = {
        "chat_id": chat_id,
        "text": (
            "StyleFlow yordam:\n\n"
            "/start — Mini App tugmasini olish\n"
            "/health — bot ishlayotganini tekshirish\n\n"
            "App ichida ro‘yxatdan o‘ting, barber tanlang va vaqt slotini bron qiling."
        ),
    }
    telegram_api("sendMessage", payload)


@app.get("/")
def root():
    return jsonify(
        {
            "success": True,
            "message": "StyleFlow Python bot is running",
            "mini_app_url_configured": bool(MINI_APP_URL),
            "backend_api_url_configured": bool(BACKEND_API_URL),
        }
    )


@app.get("/health")
def health():
    return jsonify(
        {
            "success": True,
            "message": "StyleFlow Python bot health OK",
            "bot_token_configured": bool(BOT_TOKEN),
            "mini_app_url_configured": bool(MINI_APP_URL),
        }
    )


@app.post("/api/telegram/webhook")
def telegram_webhook():
    update = request.get_json(silent=True) or {}
    logger.info("Telegram update: %s", update)

    message = update.get("message") or update.get("edited_message")
    if not message:
        return jsonify({"ok": True})

    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    text = (message.get("text") or "").strip()

    if not chat_id:
        return jsonify({"ok": True})

    if text == "/start":
        send_start_message(chat_id)
    elif text == "/help":
        send_help_message(chat_id)
    elif text == "/health":
        telegram_api("sendMessage", {"chat_id": chat_id, "text": "✅ StyleFlow bot ishlayapti."})
    else:
        telegram_api(
            "sendMessage",
            {
                "chat_id": chat_id,
                "text": "StyleFlow Mini Appni ochish uchun /start yuboring.",
            },
        )

    return jsonify({"ok": True})


@app.post("/api/notify-booking")
def notify_booking():
    """
    Optional endpoint: backend can call this endpoint to send booking notification.
    Expected JSON:
    {
      "telegram_id": 123,
      "barber_name": "Aziz Barber",
      "service_name": "Skin Fade",
      "date": "2026-05-07",
      "time": "14:30",
      "price": 95000
    }
    """
    data = request.get_json(silent=True) or {}
    telegram_id = data.get("telegram_id")

    if not telegram_id:
        return jsonify({"success": False, "message": "telegram_id is required"}), 400

    text = (
        "✅ Booking confirmed!\n\n"
        f"Barber: {data.get('barber_name', '—')}\n"
        f"Service: {data.get('service_name', '—')}\n"
        f"Date: {data.get('date', '—')}\n"
        f"Time: {data.get('time', '—')}\n"
        f"Price: {data.get('price', '—')} UZS"
    )

    result = telegram_api("sendMessage", {"chat_id": telegram_id, "text": text})
    return jsonify({"success": True, "telegram_result": result})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
