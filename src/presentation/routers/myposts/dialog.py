from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format, Multi
from aiogram_dialog.widgets.kbd import Button, Group, Back, ScrollingGroup, Select
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.media import StaticMedia

from src.presentation.states import MyPostsSG
from . import getter, on_event

# First window is for listing all posts
# Second window is for previewing the selected post

dialog = Dialog(
    Window(
        Format("📋 Ваши посты:\n\n{posts_list}"),
        Select(
            Format("{item[name]}"),
            id="posts_select",
            item_id_getter=lambda item: item["id"],
            items="posts",
            on_click=on_event.on_post_selected,
        ),
        Button(Const("◀️ Назад"), id="back", on_click=on_event.back_to_main),
        state=MyPostsSG.list,
        getter=getter.get_posts_list
    ),
    Window(
        Multi(
            Format("📝 {post_name}"),
            Format(""),
            Format("{post_text}"),
            Format(""),
            Format("Статус: {post_status}"),
            Format("{publish_date}"),
        ),
        StaticMedia(
            path=Format("{post_image}"),
            when="has_image"
        ),
        Button(Const("📋 К списку постов"), id="back_to_list", on_click=on_event.back_to_list),
        state=MyPostsSG.view,
        getter=getter.get_post_details
    )
)
