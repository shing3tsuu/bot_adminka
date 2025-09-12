from aiogram.fsm.state import State, StatesGroup

class MenuSG(StatesGroup):
    menu = State()

class MyPostsSG(StatesGroup):
    list = State()
    view = State()

class RegistrationSG(StatesGroup):
    surname = State()
    name = State()
    patronymic = State()
    phone = State()
    confirm = State()

class PostSG(StatesGroup):
    add_post = State()
    add_post_text = State()
    add_post_media = State()
    preview = State()
    confirm_publish = State()
    moderation_warning = State()
    schedule_date = State()
    schedule_time = State()

class AdminSG(StatesGroup):
    menu = State()
    link = State()
