from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format, Multi
from aiogram_dialog.widgets.kbd import Button, Group, Back, ScrollingGroup, Select
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.media import DynamicMedia


from src.presentation.states import MyPostsSG
from . import getter, on_event

# First window is for listing all posts
# Second window is for previewing the selected post

dialog = Dialog(
    Window(
        Format("📋 Ваши посты:\n\n{posts_list}"),
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
            Format("Статус модерации: {post_status}"),
            Format("{publish_date}"),
            Format(""),
            Format("Статус оплаты: {paid_status}")
        ),
        DynamicMedia("media", when="has_media"),
        Group(
            Button(
                Const("💳 Оплатить публикацию"),
                id="pay_post",
                on_click=on_event.pay_post,
                when="can_pay"
            ),
            Button(
                Const("❌ Удалить"),
                id="delete_post",
                on_click=on_event.delete_post,
                when="can_delete"
            ),
            Button(
                Const("📋 К списку постов"),
                id="back_to_list",
                on_click=on_event.back_to_list
            ),
            width=1
        ),
        state=MyPostsSG.view,
        getter=getter.get_post_details
    ),
    Window(
        Format("❌ Вы уверены, что хотите удалить пост \"{post_name}\"?\n\nЭто действие нельзя отменить."),
        Group(
            Button(Const("✅ Да, удалить"), id="confirm_delete", on_click=on_event.confirm_delete),
            Button(Const("❌ Нет, отменить"), id="cancel_delete", on_click=on_event.cancel_delete),
            width=2
        ),
        state=MyPostsSG.delete_confirm,
        getter=getter.get_delete_confirmation
    )
)
