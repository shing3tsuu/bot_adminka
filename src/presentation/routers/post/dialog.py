from aiogram import F
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import SwitchTo, Select, Group, Button, Back
from aiogram_dialog.widgets.input import TextInput, MessageInput

from src.presentation.states import PostSG
from . import on_event, getter

# Окно меню
dialog = Dialog(
    Window(
        Const("Главное меню:"),
        Button(Const("Создать пост"), id="create_post", on_click=on_event.start_create_post),
        state=PostSG.menu
    ),
    Window(
        Const("Введите название поста:"),
        TextInput(id="name_input", on_success=on_event.on_name_entered),
        Back(Const("Назад")),
        state=PostSG.add_post
    ),
    Window(
        Const("Введите текст поста:"),
        TextInput(id="text_input", on_success=on_event.on_text_entered),
        Back(Const("Назад")),
        state=PostSG.add_post_text
    ),
    Window(
        Const("Отправьте изображение (опционально):"),
        MessageInput(on_event.on_image_sent),
        Button(Const("Пропустить"), id="skip_image", on_click=on_event.on_skip_image),
        Back(Const("Назад")),
        state=PostSG.add_post_image
    )
)