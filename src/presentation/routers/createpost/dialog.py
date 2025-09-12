from aiogram import F
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import SwitchTo, Select, Group, Button, Back, Row, Calendar
from aiogram_dialog.widgets.input import TextInput, MessageInput

from src.presentation.states import PostSG
from . import on_event, getter

# This is a dialog of the post creation process.
# First window is for entering the post name,
# Second window is for entering the post text,
# Third window is for uploading media (optional)
# Fourth window is for previewing the post
# Fifth window is for editing the post text if there are banned words
# Sixth window is for definition, if the post should be published immediately or scheduled
# Seventh window is for selecting the date of publication (day:month:year)
# Eighth window is for entering the time of publication (hour:minute)

# development tasks: add payment for creating posts

dialog = Dialog(
    Window(
        Const("Введите название поста:"),
        TextInput(id="name_input", on_success=on_event.on_name_entered),
        Button(Const("◀️ Назад"), id="back", on_click=on_event.back_to_main),
        state=PostSG.add_post
    ),
    Window(
        Const("Введите текст поста:"),
        TextInput(id="text_input", on_success=on_event.on_text_entered),
        Back(Const("Назад")),
        state=PostSG.add_post_text
    ),
    Window(
        Const("Отправьте изображение или видео (опционально):"),
        MessageInput(on_event.on_media_sent),
        Button(Const("Пропустить"), id="skip_media", on_click=on_event.on_skip_media),
        Back(Const("◀️ Назад")),
        Back(Const("Назад")),
        state=PostSG.add_post_media
    ),
    Window(
        Format("Предпросмотр поста:\n\n"
               "Название: {name}\n"
               "Текст: {text}\n"
               "Медиа: {media_status}\n\n"
               "Всё верно?"),
        Group(
            Button(Const("✅ Да, продолжить"), id="confirm_preview", on_click=on_event.on_confirm_preview),
            Button(Const("❌ Нет, изменить"), id="edit_post", on_click=on_event.on_edit_post),
        ),
        state=PostSG.preview,
        getter=getter.get_preview_data
    ),
    Window(
        Format("Обнаружены запрещенные слова в тексте:\n\n"
               "{banned_words}\n\n"
               "Пожалуйста, исправьте текст перед публикацией."),
        Button(Const("◀️ Исправить текст"), id="edit_text", on_click=on_event.on_edit_text),
        state=PostSG.moderation_warning
    ),
    Window(
        Const("Опубликовать пост сейчас или запланировать публикацию?"),
        Group(
            Button(Const("Опубликовать сейчас"), id="publish_now", on_click=on_event.on_publish_now),
            Button(Const("Запланировать публикацию"), id="schedule_post", on_click=on_event.on_schedule_post)
        ),
        state=PostSG.confirm_publish
    ),
    Window(
        Const("Выберите дату публикации:"),
        Calendar(
            id="calendar",
            on_click=on_event.on_date_selected
        ),
        Back(Const("Назад")),
        state=PostSG.schedule_date
    ),
    Window(
        Const("Введите время публикации в формате ЧЧ:ММ (например, 13:00):"),
        TextInput(id="time_input", on_success=on_event.on_time_entered),
        Back(Const("Назад")),
        state=PostSG.schedule_time
    )
)