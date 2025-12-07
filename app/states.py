from enum import Enum

from aiogram.dispatcher.filters.state import State, StatesGroup


class Lang(str, Enum):
    RU = "ru"
    EN = "en"


class LeadForm(StatesGroup):
    LANG = State()
    NAME = State()
    SERVICE = State()
    AUTO_MAKE = State()
    AUTO_MODEL = State()
    AUTO_YEAR = State()
    MESSAGE = State()
    EMAIL = State()
    PHONE = State()
