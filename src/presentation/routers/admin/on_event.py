from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from dishka.integrations.aiogram_dialog import inject
from typing import Any
from dishka import FromDishka

from src.presentation.states import AdminSG
from src.adapters.database.service import PostService, PriceService


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
        price_service: FromDishka[PriceService]
):
    try:
        new_price = int(message.text)
        if new_price <= 0:
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
        post_service: FromDishka[PostService]
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
        post_service: FromDishka[PostService]
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
        post_service: FromDishka[PostService]
):
    posts = dialog_manager.dialog_data.get("posts", [])
    current_index = dialog_manager.dialog_data.get("current_index", 0)

    if current_index < len(posts):
        post = posts[current_index]
        await post_service.reject_post(post['id'])
        await callback.message.answer("Пост отклонен.")

    await dialog_manager.switch_to(AdminSG.moderation_list)
