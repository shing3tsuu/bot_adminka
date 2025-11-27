from aiogram.fsm.state import State, StatesGroup

class MenuSG(StatesGroup):
    menu = State()

class MyPostsSG(StatesGroup):
    list = State()
    view = State()
    delete_confirm = State()

class RegistrationSG(StatesGroup):
    surname = State()
    name = State()
    patronymic = State()
    phone = State()
    organization = State()
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
    publish_limit_warning = State()

class AdminSG(StatesGroup):
    menu = State()
    moderation_list = State()
    review_post = State()
    change_price = State()
    users_list = State()
    user_detail = State()
    user_approval = State()
    all_users_list = State()
    all_user_detail = State()
    search_users = State()
    search_results = State()