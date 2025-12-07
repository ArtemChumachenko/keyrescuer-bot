import os
import logging
import aiohttp
from aiogram import types


async def log_dialog(
    message: types.Message | None = None,
    step: str = "",
    language: str = "",
    source: str = "telegram-bot",
    text: str | None = None,
    user: types.User | None = None,
):
    """
    Логирует одно сообщение клиента в Google Sheets через Apps Script (mode=dialog_log).
    Допускает вызов без aiogram Message (для callback), если передать user + text.
    """
    apps_script_url = os.getenv("APPS_SCRIPT_URL")
    if not apps_script_url:
        logging.warning("APPS_SCRIPT_URL is not set; dialog will not be logged")
        return

    user_obj = user or (message.from_user if message else None)
    if not user_obj:
        logging.warning("log_dialog: user is missing; skip log")
        return

    msg_text = text
    if msg_text is None:
        msg_text = (message.text or "") if message else ""

    payload = {
        "mode": "dialog_log",
        "source": source,
        "user_id": user_obj.id,
        "username": user_obj.username or "",
        "first_name": user_obj.first_name or "",
        "last_name": user_obj.last_name or "",
        "language": language or (getattr(user_obj, "language_code", "") or ""),
        "step": step or "",
        "message": msg_text,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(apps_script_url, data=payload) as resp:
                if resp.status != 200:
                    logging.error(f"Dialog log failed: HTTP {resp.status}")
                else:
                    logging.info(f"Dialog logged (step={payload['step']}): {payload['message']}")
    except Exception as e:
        logging.error(f"Error sending dialog log to Apps Script: {e}")
