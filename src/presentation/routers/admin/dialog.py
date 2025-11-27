from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format, Multi
from aiogram_dialog.widgets.kbd import Button, Group, Back, Select, Cancel
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.input import TextInput, MessageInput

from src.presentation.states import AdminSG
from . import getter, on_event

dialog = Dialog(
    Window(
        Const("Меню администрирования"),
        Group(
            Button(Const("Модерация постов"), id="moderation", on_click=on_event.on_moderation),
            Button(Const("Верификация пользователей"), id="user_management", on_click=on_event.on_user_management),
            Button(Const("Все пользователи"), id="all_users", on_click=on_event.on_all_users),  # Новая кнопка
            Button(Const("Изменить цену публикации"), id="change_price", on_click=on_event.on_change_price),
            width=1
        ),
        state=AdminSG.menu,
    ),
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
        Back(Const("◀️ Назад")),
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
            Back(Const("◀️ Назад")),
        ),
        state=AdminSG.review_post,
        getter=getter.get_post_details
    ),
    Window(
        Format("Текущая цена: {current_price} руб.\n\nВведите новую цену:"),
        MessageInput(on_event.on_price_input),
        Back(Const("◀️ Назад")),
        state=AdminSG.change_price,
        getter=getter.get_current_price
    ),
    Window(
        Format("Пользователи:\n\n{users_list}"),
        Group(
            Select(
                Format("{item[name]}"),
                id="users_select",
                item_id_getter=lambda item: item["id"],
                items="users",
                on_click=on_event.on_user_selected
            ),
            width=1
        ),
        Back(Const("◀️ Назад")),
        state=AdminSG.users_list,
        getter=getter.get_users_list
    ),
    Window(
        Multi(
            Format("👤 {user_name}"),
            Format(""),
            Format("Телефон: {user_phone}"),
            Format(""),
            Format("Статус: {user_status}"),
            Format("Админ: {is_admin}"),
        ),
        Group(
            Button(Const("✅ Подтвердить"), id="approve_user", on_click=on_event.on_approve_user),
            Back(Const("◀️ Назад")),
        ),
        state=AdminSG.user_detail,
        getter=getter.get_user_details
    ),
    Window(
        Format("Все пользователи:\n\n{all_users_list}"),
        Group(
            Select(
                Format("{item[name]}"),
                id="all_users_select",
                item_id_getter=lambda item: item["id"],
                items="all_users",
                on_click=on_event.on_all_user_selected
            ),
            width=1
        ),
        Group(
            Button(Const("◀️ Предыдущая"), id="prev_page", on_click=on_event.on_all_users_previous_page,
                   when="has_previous"),
            Button(Const("Следующая ▶️"), id="next_page", on_click=on_event.on_all_users_next_page, when="has_next"),
            width=2
        ),
        Group(
            Button(Const("🔍 Поиск"), id="search_users", on_click=on_event.on_search_users),
            width=1
        ),
        Back(Const("◀️ Назад")),
        state=AdminSG.all_users_list,
        getter=getter.get_all_users_list
    ),
    Window(
        Multi(
            Format("👤 {user_name}"),
            Format(""),
            Format("Telegram: {user_tg_username}"),
            Format("ID: {user_tg_id}"),
            Format("Телефон: {user_phone}"),
            Format(""),
            Format("Статус: {user_status}"),
            Format("Админ: {is_admin}"),
            Format("Подтвержден: {is_approved}"),
            Format(""),
            Format("Статистика постов:"),
            Format("{posts_info}"),
        ),
        Group(
            Button(Const("◀️ Назад"), id="back_from_detail", on_click=on_event.on_back_from_user_detail),
            width=1
        ),
        Group(
            Back(Const("◀️ Назад к списку")),
            width=1
        ),
        state=AdminSG.all_user_detail,
        getter=getter.get_all_user_details
    ),
    Window(
        Const("🔍 Введите ФИО или часть имени для поиска:"),
        MessageInput(on_event.on_search_input),
        Back(Const("◀️ Назад")),
        state=AdminSG.search_users
    ),
    Window(
        Format("{search_results_list}"),
        Group(
            Select(
                Format("{item[name]}"),
                id="search_results_select",
                item_id_getter=lambda item: item["id"],
                items="search_results",
                on_click=on_event.on_searched_user_selected
            ),
            width=1
        ),
        Back(Const("◀️ Новый поиск")),
        state=AdminSG.search_results,
        getter=getter.get_search_results
    ),
)