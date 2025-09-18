from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format, Multi
from aiogram_dialog.widgets.kbd import Button, Group, Back, Select, Cancel
from aiogram_dialog.widgets.media import DynamicMedia

from src.presentation.states import AdminSG
from . import getter, on_event

dialog = Dialog(
    Window(
        Format("Посты на модерации:\n\n{posts_list}"),
        Group(
            Select(
                Format("{item[name]}"),
                id="posts_select",
                item_id_getter=lambda item: item["id"],
                items="posts",
                on_click=on_event.on_post_selected
            ),
            width=1
        ),
        Cancel(Const("◀️ Назад")),
        state=AdminSG.moderation_list,
        getter=getter.get_posts_list
    ),
    Window(
        Multi(
            Format("📝 {post_name}"),
            Format(""),
            Format("{post_text}"),
            Format(""),
            Format("Отправитель: {sender_name}"),
            Format("Телефон: {sender_phone}"),
            Format(""),
            Format("Статус: {post_status}"),
        ),
        DynamicMedia("media", when="has_media"),
        Group(
            Button(Const("✅ Одобрить"), id="approve_post", on_click=on_event.on_approve_post),
            Button(Const("❌ Отклонить"), id="reject_post", on_click=on_event.on_reject_post),
            Button(Const("◀️ Назад"), id="back_to_list", on_click=on_event.back_to_list),
        ),
        state=AdminSG.review_post,
        getter=getter.get_post_details
    )
)
