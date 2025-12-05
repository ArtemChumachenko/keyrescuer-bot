from aiogram import types

from .states import Lang


def t(lang: Lang, key: str) -> str:
    texts = {
        "start": {
            Lang.RU: (
                "Привет!!!!!!!!!!!!!!!!! Я бот KeyRescuer.\n"
                "Я помогу оформить заявку на выезд локсмита.\n\n"
                "Пожалуйста, выберите язык:"
            ),
            Lang.EN: (
                "Hi!!!!!!!!!!!!!!!!!! I'm the KeyRescuer bot.\n"
                "I will help you create a locksmith service request.\n\n"
                "Please choose your language:"
            ),
        },
        "ask_name": {
            Lang.RU: "Как вас зовут?",
            Lang.EN: "What is your name?",
        },
        "ask_phone": {
            Lang.RU: "Укажите, пожалуйста, номер телефона:",
            Lang.EN: "Please enter your phone number:",
        },
        "ask_email": {
            Lang.RU: "Укажите, пожалуйста, email (или напишите «нет»):",
            Lang.EN: "Please enter your email (or type 'no'):",
        },
        "ask_message": {
            Lang.RU: "Коротко опишите ситуацию (дверь/авто/замок и т.п.):",
            Lang.EN: "Briefly describe your situation (door/car/lock etc.):",
        },
        "thanks": {
            Lang.RU: (
                "Спасибо! Ваша заявка отправлена.\n"
                "Мы свяжемся с вами как можно скорее."
            ),
            Lang.EN: (
                "Thank you! Your request has been sent.\n"
                "We will contact you as soon as possible."
            ),
        },
        "error_send": {
            Lang.RU: "Произошла ошибка при отправке заявки. Попробуйте ещё раз позже.",
            Lang.EN: "An error occurred while sending your request. Please try again later.",
        },
        "restart_hint": {
            Lang.RU: "Если хотите оформить новую заявку — отправьте команду /start.",
            Lang.EN: "If you want to create a new request, send /start.",
        },
        "cancel": {
            Lang.RU: "Диалог отменён. Чтобы начать заново — отправьте /start.",
            Lang.EN: "Conversation cancelled. To start again, send /start.",
        },
    }
    return texts[key][lang]


def language_keyboard() -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        types.InlineKeyboardButton("🇺🇸 English", callback_data="lang_en"),
    )
    return kb
