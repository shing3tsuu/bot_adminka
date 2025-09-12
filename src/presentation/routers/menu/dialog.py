from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.kbd import Button, Group

from src.presentation.states import MenuSG
from . import on_event

# This is a dialog for the main menu

dialog = Dialog(
    Window(
        Const("🏠 Главное меню\n\nВыберите действие:"),
        Group(
            Button(Const("📝 Создать пост"), id="create_post", on_click=on_event.start_create_post),
            Button(Const("📋 Мои посты"), id="my_posts", on_click=on_event.show_my_posts),
            Button(Const("ℹ️ Информация о боте"), id="info", on_click=on_event.show_info),
            width=1
        ),
        state=MenuSG.menu
    )
)