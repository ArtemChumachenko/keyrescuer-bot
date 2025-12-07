import logging
import os
from logging.handlers import RotatingFileHandler

import requests
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from dotenv import load_dotenv

from .states import Lang, LeadForm
from .texts import language_keyboard, service_keyboard, t

LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOGS_DIR, "bot.log")
log_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

file_handler = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=5, encoding="utf-8")
file_handler.setFormatter(log_formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_formatter)

logging.basicConfig(level=logging.INFO, handlers=[file_handler, stream_handler])
logger = logging.getLogger(__name__)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
APPS_SCRIPT_URL = os.getenv("APPS_SCRIPT_URL")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

AUTO_MAKES = [
    "Toyota",
    "Honda",
    "Ford",
    "Chevrolet",
    "BMW",
    "Mercedes-Benz",
    "Audi",
    "Volkswagen",
    "Hyundai",
    "Kia",
    "Nissan",
    "Subaru",
]

AUTO_MODELS = {
    "Toyota": ["Camry", "Corolla", "RAV4", "Highlander", "4Runner", "Tacoma"],
    "Honda": ["Accord", "Civic", "CR-V", "Pilot", "Odyssey", "Ridgeline"],
    "Ford": ["F-150", "Escape", "Explorer", "Focus", "Fusion", "Bronco"],
    "Chevrolet": ["Silverado", "Equinox", "Tahoe", "Malibu", "Traverse", "Camaro"],
    "BMW": ["3 Series", "5 Series", "X3", "X5", "X6", "1 Series"],
    "Mercedes-Benz": ["C-Class", "E-Class", "S-Class", "GLC", "GLE", "GLA"],
    "Audi": ["A3", "A4", "A6", "Q3", "Q5", "Q7"],
    "Volkswagen": ["Golf", "Passat", "Tiguan", "Atlas", "Jetta", "Taos"],
    "Hyundai": ["Elantra", "Sonata", "Tucson", "Santa Fe", "Kona", "Palisade"],
    "Kia": ["Rio", "Forte", "Optima", "Sportage", "Sorento", "Telluride"],
    "Nissan": ["Sentra", "Altima", "Maxima", "Rogue", "Murano", "Pathfinder"],
    "Subaru": ["Impreza", "Legacy", "Outback", "Forester", "Ascent", "Crosstrek"],
}

AUTO_YEARS = [str(year) for year in range(2024, 2009, -1)]
PAGE_SIZE = 6

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set in .env")
if not APPS_SCRIPT_URL:
    raise RuntimeError("APPS_SCRIPT_URL is not set in .env")

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


def paginated_keyboard(items: list[str], prefix: str, page: int) -> types.InlineKeyboardMarkup:
    """Builds inline keyboard with pagination for long lists."""
    kb = types.InlineKeyboardMarkup()
    start = page * PAGE_SIZE
    chunk = items[start : start + PAGE_SIZE]

    for item in chunk:
        kb.add(types.InlineKeyboardButton(item, callback_data=f"{prefix}:select:{item}"))

    nav_buttons = []
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton("⬅️", callback_data=f"{prefix}:page:{page - 1}"))
    if start + PAGE_SIZE < len(items):
        nav_buttons.append(types.InlineKeyboardButton("➡️", callback_data=f"{prefix}:page:{page + 1}"))
    if nav_buttons:
        kb.row(*nav_buttons)
    return kb


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    # Показываем приветствие на двух языках, используя тексты из app/texts.py
    text = f"{t(Lang.EN, 'start')}\n\n{t(Lang.RU, 'start')}"
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
    await message.answer(t(lang, "ask_service"), reply_markup=service_keyboard(lang))
    await LeadForm.SERVICE.set()


@dp.callback_query_handler(lambda c: c.data.startswith("service_"), state=LeadForm.SERVICE)
async def process_service(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang: Lang = data.get("lang", Lang.EN)
    service = callback_query.data.replace("service_", "")

    await state.update_data(service=service)
    await bot.answer_callback_query(callback_query.id)

    if service == "auto":
        kb = paginated_keyboard(AUTO_MAKES, "auto_make", 0)
        await bot.send_message(callback_query.from_user.id, t(lang, "ask_auto_make"), reply_markup=kb)
        await LeadForm.AUTO_MAKE.set()
    else:
        await bot.send_message(callback_query.from_user.id, t(lang, "ask_message"))
        await LeadForm.MESSAGE.set()


@dp.callback_query_handler(lambda c: c.data.startswith("auto_make:"), state=LeadForm.AUTO_MAKE)
async def process_auto_make(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang: Lang = data.get("lang", Lang.EN)
    _, action, value = callback_query.data.split(":", 2)

    if action == "page":
        page = int(value)
        kb = paginated_keyboard(AUTO_MAKES, "auto_make", page)
        await bot.answer_callback_query(callback_query.id)
        await callback_query.message.edit_reply_markup(reply_markup=kb)
        return

    auto_make = value
    await state.update_data(auto_make=auto_make)
    models = AUTO_MODELS.get(auto_make, [])
    kb = paginated_keyboard(models or ["Other"], "auto_model", 0)

    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, t(lang, "ask_auto_model"), reply_markup=kb)
    await LeadForm.AUTO_MODEL.set()


@dp.callback_query_handler(lambda c: c.data.startswith("auto_model:"), state=LeadForm.AUTO_MODEL)
async def process_auto_model(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang: Lang = data.get("lang", Lang.EN)
    _, action, value = callback_query.data.split(":", 2)

    if action == "page":
        page = int(value)
        auto_make = data.get("auto_make", "")
        models = AUTO_MODELS.get(auto_make, [])
        kb = paginated_keyboard(models or ["Other"], "auto_model", page)
        await bot.answer_callback_query(callback_query.id)
        await callback_query.message.edit_reply_markup(reply_markup=kb)
        return

    auto_model = value
    await state.update_data(auto_model=auto_model)
    kb = paginated_keyboard(AUTO_YEARS, "auto_year", 0)

    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, t(lang, "ask_auto_year"), reply_markup=kb)
    await LeadForm.AUTO_YEAR.set()


@dp.callback_query_handler(lambda c: c.data.startswith("auto_year:"), state=LeadForm.AUTO_YEAR)
async def process_auto_year(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang: Lang = data.get("lang", Lang.EN)
    _, action, value = callback_query.data.split(":", 2)

    if action == "page":
        page = int(value)
        kb = paginated_keyboard(AUTO_YEARS, "auto_year", page)
        await bot.answer_callback_query(callback_query.id)
        await callback_query.message.edit_reply_markup(reply_markup=kb)
        return

    await state.update_data(auto_year=value)
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, t(lang, "ask_message"))
    await LeadForm.MESSAGE.set()


@dp.message_handler(state=LeadForm.PHONE)
async def process_phone(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang: Lang = data.get("lang", Lang.EN)

    await state.update_data(phone=(message.text or "").strip())
    data = await state.get_data()

    name = data.get("name", "")
    service = data.get("service", "")
    auto_make = data.get("auto_make", "")
    auto_model = data.get("auto_model", "")
    auto_year = data.get("auto_year", "")
    email = data.get("email", "")
    msg = data.get("message", "")

    service_label = {
        "auto": t(lang, "service_auto"),
        "home": t(lang, "service_home"),
        "office": t(lang, "service_office"),
    }.get(service, service)

    payload = {
        "name": name,
        "email": email,
        "phone": data.get("phone", ""),
        "message": msg,
        "service": service_label,
        "auto_make": auto_make,
        "auto_model": auto_model,
        "auto_year": auto_year,
        "source": "telegram-bot",
        "lang": lang.value,
        "user_id": message.from_user.id,
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


@dp.message_handler(state=LeadForm.EMAIL)
async def process_email(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang: Lang = data.get("lang", Lang.EN)

    email = (message.text or "").strip()
    if email.lower() in ["нет", "no", "none", "n/a", "не знаю"]:
        email = ""

    await state.update_data(email=email)
    await message.answer(t(lang, "ask_phone"))
    await LeadForm.PHONE.set()


@dp.message_handler(state=LeadForm.MESSAGE)
async def process_message(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang: Lang = data.get("lang", Lang.EN)

    await state.update_data(message=(message.text or "").strip())
    await message.answer(t(lang, "ask_email"))
    await LeadForm.EMAIL.set()


@dp.message_handler()
async def fallback(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", Lang.EN)
    await message.answer(t(lang, "restart_hint"))


if __name__ == "__main__":
    logger.info("KeyRescuer aiogram bot started (local).")
    executor.start_polling(dp, skip_updates=True)
