import logging
import os

import requests
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from dotenv import load_dotenv

from .states import Lang, LeadForm
from .texts import language_keyboard, t

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
APPS_SCRIPT_URL = os.getenv("APPS_SCRIPT_URL")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set in .env")
if not APPS_SCRIPT_URL:
    raise RuntimeError("APPS_SCRIPT_URL is not set in .env")

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    text = (
        "KeyRescuer — mobile locksmith service.\n\n"
        "KeyRescuer — мобильный сервис по вскрытию и замене замков.\n\n"
        "Please choose your language / Пожалуйста, выберите язык:"
    )
    await message.answer(text, reply_markup=language_keyboard())
    await LeadForm.LANG.set()


@dp.message_handler(commands=["cancel"], state="*")
async def cmd_cancel(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", Lang.EN)
    await message.answer(t(lang, "cancel"))
    await state.finish()


@dp.callback_query_handler(lambda c: c.data in ("lang_ru", "lang_en"), state=LeadForm.LANG)
async def process_language(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == "lang_ru":
        lang = Lang.RU
    else:
        lang = Lang.EN

    await state.update_data(lang=lang)
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, t(lang, "ask_name"))
    await LeadForm.NAME.set()


@dp.message_handler(state=LeadForm.NAME)
async def process_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang: Lang = data.get("lang", Lang.EN)

    await state.update_data(name=(message.text or "").strip())
    await message.answer(t(lang, "ask_phone"))
    await LeadForm.PHONE.set()


@dp.message_handler(state=LeadForm.PHONE)
async def process_phone(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang: Lang = data.get("lang", Lang.EN)

    await state.update_data(phone=(message.text or "").strip())
    await message.answer(t(lang, "ask_email"))
    await LeadForm.EMAIL.set()


@dp.message_handler(state=LeadForm.EMAIL)
async def process_email(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang: Lang = data.get("lang", Lang.EN)

    email = (message.text or "").strip()
    if email.lower() in ["нет", "no", "none", "n/a", "не знаю"]:
        email = ""

    await state.update_data(email=email)
    await message.answer(t(lang, "ask_message"))
    await LeadForm.MESSAGE.set()


@dp.message_handler(state=LeadForm.MESSAGE)
async def process_message(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang: Lang = data.get("lang", Lang.EN)

    await state.update_data(message=(message.text or "").strip())
    data = await state.get_data()

    name = data.get("name", "")
    phone = data.get("phone", "")
    email = data.get("email", "")
    msg = data.get("message", "")

    payload = {
        "name": name,
        "email": email,
        "phone": phone,
        "message": msg,
        "source": "telegram-bot",
    }

    try:
        resp = requests.post(APPS_SCRIPT_URL, data=payload, timeout=10)
        resp.raise_for_status()
        logger.info("Sent lead to Apps Script: %s", resp.text[:200])
    except Exception as e:
        logger.exception("Error sending data to Apps Script: %s", e)
        await message.answer(t(lang, "error_send"))
        await message.answer(t(lang, "restart_hint"))
        await state.finish()
        return

    await message.answer(t(lang, "thanks"))
    await message.answer(t(lang, "restart_hint"))

    await state.finish()


@dp.message_handler()
async def fallback(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", Lang.EN)
    await message.answer(t(lang, "restart_hint"))


if __name__ == "__main__":
    logger.info("KeyRescuer aiogram bot started (local).")
    executor.start_polling(dp, skip_updates=True)
