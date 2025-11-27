from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from dishka.integrations.aiogram_dialog import inject
from typing import Any
from dishka import FromDishka

from src.presentation.states import AdminSG
from src.adapters.database.service import AbstractUserService, AbstractPostService, AbstractPriceService

async def on_user_management(
        callback: CallbackQuery,
        widget: Any,
        dialog_manager: DialogManager
):
    await dialog_manager.switch_to(AdminSG.users_list)

@inject
async def on_user_selected(
        callback: CallbackQuery,
        widget: Any,
        dialog_manager: DialogManager,
        item_id: str,
        user_service: FromDishka[AbstractUserService]
):
    dialog_manager.dialog_data["current_user_index"] = int(item_id)
    await dialog_manager.switch_to(AdminSG.user_detail)


@inject
async def on_approve_user(
        callback: CallbackQuery,
        widget: Any,
        dialog_manager: DialogManager,
        user_service: FromDishka[AbstractUserService]
):
    users = dialog_manager.dialog_data.get("users", [])
    current_index = dialog_manager.dialog_data.get("current_user_index", 0)

    if current_index < len(users):
        user = users[current_index]
        await user_service.approve_user(user['id'])
        await callback.message.answer("Пользователь подтвержден.")

    await dialog_manager.switch_to(AdminSG.users_list)


@inject
async def on_revoke_approval(
        callback: CallbackQuery,
        widget: Any,
        dialog_manager: DialogManager,
        user_service: FromDishka[AbstractUserService]
):
    users = dialog_manager.dialog_data.get("users", [])
    current_index = dialog_manager.dialog_data.get("current_user_index", 0)

    if current_index < len(users):
        user = users[current_index]
        # TODO: Добавить бизнес-логику для отзыва подтверждения
        # await user_service.revoke_user_approval(user['id'])
        await callback.message.answer("Подтверждение пользователя отозвано.")

    await dialog_manager.switch_to(AdminSG.user_list)

async def on_moderation(
        callback: CallbackQuery,
        widget: Any,
        dialog_manager: DialogManager
):
    await dialog_manager.switch_to(AdminSG.moderation_list)

async def on_change_price(
        callback: CallbackQuery,
        widget: Any,
        dialog_manager: DialogManager
):
    await dialog_manager.switch_to(AdminSG.change_price)

@inject
async def on_price_input(
        message: Message,
        widget: Any,
        dialog_manager: DialogManager,
        price_service: FromDishka[AbstractPriceService]
):
    try:
        new_price = int(message.text)
        if new_price < 0:
            await message.answer("Цена должна быть положительным числом.")
            return
    except ValueError:
        await message.answer("Пожалуйста, введите целое число.")
        return

    await price_service.change_price(name="default", price=new_price)
    await message.answer(f"Цена успешно изменена на {new_price} руб.")
    await dialog_manager.switch_to(AdminSG.menu)


@inject
async def on_post_selected(
        callback: CallbackQuery,
        widget: Any,
        dialog_manager: DialogManager,
        item_id: str,
        post_service: FromDishka[AbstractPostService]
):
    dialog_manager.dialog_data["current_index"] = int(item_id)
    await dialog_manager.switch_to(AdminSG.review_post)

@inject
async def back_to_list(
        callback: CallbackQuery,
        widget: Any,
        dialog_manager: DialogManager
):
    await dialog_manager.switch_to(AdminSG.moderation_list)


@inject
async def on_approve_post(
        callback: CallbackQuery,
        widget: Any,
        dialog_manager: DialogManager,
        post_service: FromDishka[AbstractPostService]
):
    posts = dialog_manager.dialog_data.get("posts", [])
    current_index = dialog_manager.dialog_data.get("current_index", 0)

    if current_index < len(posts):
        post = posts[current_index]
        await post_service.approve_post(post['id'])
        await callback.message.answer("Пост одобрен.")

    await dialog_manager.switch_to(AdminSG.moderation_list)


@inject
async def on_reject_post(
        callback: CallbackQuery,
        widget: Any,
        dialog_manager: DialogManager,
        post_service: FromDishka[AbstractPostService]
):
    posts = dialog_manager.dialog_data.get("posts", [])
    current_index = dialog_manager.dialog_data.get("current_index", 0)

    if current_index < len(posts):
        post = posts[current_index]
        await post_service.reject_post(post['id'])
        await callback.message.answer("Пост отклонен.")

    await dialog_manager.switch_to(AdminSG.moderation_list)

async def on_all_users(
        callback: CallbackQuery,
        widget: Any,
        dialog_manager: DialogManager
):
    dialog_manager.dialog_data["all_users_page"] = 0
    await dialog_manager.switch_to(AdminSG.all_users_list)

@inject
async def on_all_user_selected(
        callback: CallbackQuery,
        widget: Any,
        dialog_manager: DialogManager,
        item_id: str,
        user_service: FromDishka[AbstractUserService]
):
    dialog_manager.dialog_data["all_users_current_index"] = int(item_id)
    await dialog_manager.switch_to(AdminSG.all_user_detail)

async def on_all_users_previous_page(
        callback: CallbackQuery,
        widget: Any,
        dialog_manager: DialogManager
):
    current_page = dialog_manager.dialog_data.get("all_users_page", 0)
    if current_page > 0:
        dialog_manager.dialog_data["all_users_page"] = current_page - 1
    await dialog_manager.switch_to(AdminSG.all_users_list)

async def on_all_users_next_page(
        callback: CallbackQuery,
        widget: Any,
        dialog_manager: DialogManager
):
    current_page = dialog_manager.dialog_data.get("all_users_page", 0)
    total_pages = dialog_manager.dialog_data.get("all_users_total_pages", 1)
    if current_page < total_pages - 1:
        dialog_manager.dialog_data["all_users_page"] = current_page + 1
    await dialog_manager.switch_to(AdminSG.all_users_list)

async def on_search_users(
        callback: CallbackQuery,
        widget: Any,
        dialog_manager: DialogManager
):
    await dialog_manager.switch_to(AdminSG.search_users)

@inject
async def on_search_input(
        message: Message,
        widget: Any,
        dialog_manager: DialogManager,
        user_service: FromDishka[AbstractUserService]
):
    search_string = message.text
    if not search_string:
        await message.answer("Введите строку для поиска.")
        return

    dialog_manager.dialog_data["search_query"] = search_string
    await dialog_manager.switch_to(AdminSG.search_results)


@inject
async def on_searched_user_selected(
        callback: CallbackQuery,
        widget: Any,
        dialog_manager: DialogManager,
        item_id: str,
        user_service: FromDishka[AbstractUserService]
):
    dialog_manager.dialog_data["searched_user_index"] = int(item_id)
    await dialog_manager.switch_to(AdminSG.all_user_detail)


async def on_back_from_user_detail(
        callback: CallbackQuery,
        widget: Any,
        dialog_manager: DialogManager
):
    source = dialog_manager.dialog_data.get("current_detail_source", "normal")

    if source == "search":
        await dialog_manager.switch_to(AdminSG.search_results)
    else:
        await dialog_manager.switch_to(AdminSG.all_users_list)