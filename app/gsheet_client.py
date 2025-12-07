import os
import logging
import aiohttp
from aiogram import types

APPS_SCRIPT_URL = os.getenv("APPS_SCRIPT_URL")  # у тебя уже должен быть в .env


async def log_dialog(
    message: types.Message,
    step: str = "",
    language: str = "",
    source: str = "telegram-bot",
):
    """
    Логирует одно сообщение клиента в Google Sheets через Apps Script (mode=dialog_log).
    """
    if not APPS_SCRIPT_URL:
        logging.warning("APPS_SCRIPT_URL is not set; dialog will not be logged")
        return

    user = message.from_user

    payload = {
        "mode": "dialog_log",
        "source": source,
        "user_id": user.id,
        "username": user.username or "",
        "first_name": user.first_name or "",
        "last_name": user.last_name or "",
        "language": language or (user.language_code or ""),
        "step": step or "",
        "message": message.text or "",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(APPS_SCRIPT_URL, data=payload) as resp:
                if resp.status != 200:
                    logging.error(f"Dialog log failed: HTTP {resp.status}")
                else:
                    logging.info(f"Dialog logged (step={payload['step']}): {payload['message']}")
    except Exception as e:
        logging.error(f"Error sending dialog log to Apps Script: {e}")
