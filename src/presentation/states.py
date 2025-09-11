from aiogram.fsm.state import State, StatesGroup

class RegistrationSG(StatesGroup):
    surname = State()
    name = State()
    patronymic = State()
    phone = State()
    confirm = State()

class PostSG(StatesGroup):
    menu = State()
    add_post = State()
    add_post_text = State()
    add_post_image = State()

class AdminSG(StatesGroup):
    menu = State()
    link = State()