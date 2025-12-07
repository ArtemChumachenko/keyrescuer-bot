from aiogram import types

from .states import Lang


def t(lang: Lang, key: str) -> str:
    texts = {
        "start": {
            Lang.RU: (
                "Привет! Я бот KeyRescuer.\n"
                "Я помогу оформить заявку на выезд локсмита.\n\n"
                "Пожалуйста, выберите язык:"
            ),
            Lang.EN: (
                "Hi! I'm the KeyRescuer bot.\n"
                "I will help you create a locksmith service request.\n\n"
                "Please choose your language:"
            ),
        },
        "ask_name": {
            Lang.RU: "Как вас зовут?",
            Lang.EN: "What is your name?",
        },
        "ask_service": {
            Lang.RU: "Какие локсмит услуги вам нужны?",
            Lang.EN: "Which locksmith service do you need?",
        },
        "service_auto": {
            Lang.RU: "Авто",
            Lang.EN: "Automotive",
        },
        "service_home": {
            Lang.RU: "Дом",
            Lang.EN: "Residential",
        },
        "service_office": {
            Lang.RU: "Офис",
            Lang.EN: "Commercial",
        },
        "ask_auto_make": {
            Lang.RU: "Выберите марку авто:",
            Lang.EN: "Select your car make:",
        },
        "ask_auto_model": {
            Lang.RU: "Выберите модель авто:",
            Lang.EN: "Select your car model:",
        },
        "ask_auto_year": {
            Lang.RU: "Укажите год выпуска авто:",
            Lang.EN: "Choose your car year:",
        },
        "ask_phone": {
            Lang.RU: "Укажите, пожалуйста, номер телефона:",
            Lang.EN: "Please enter your phone number:",
        },
        "ask_email": {
            Lang.RU: "Укажите, пожалуйста, email:",
            Lang.EN: "Please enter your email:",
        },
        "ask_message": {
            Lang.RU: "Опишите свою ситуацию, что конкретно случилось:",
            Lang.EN: "Describe your situation, what exactly happened:",
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


def service_keyboard(lang: Lang) -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton(t(lang, "service_auto"), callback_data="service_auto"),
        types.InlineKeyboardButton(t(lang, "service_home"), callback_data="service_home"),
        types.InlineKeyboardButton(t(lang, "service_office"), callback_data="service_office"),
    )
    return kb
