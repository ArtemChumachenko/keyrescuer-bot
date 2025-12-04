from enum import Enum

from aiogram.dispatcher.filters.state import State, StatesGroup


class Lang(str, Enum):
    RU = "ru"
    EN = "en"


class LeadForm(StatesGroup):
    LANG = State()
    NAME = State()
    PHONE = State()
    EMAIL = State()
    MESSAGE = State()
