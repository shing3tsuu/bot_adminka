from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from dishka.integrations.aiogram_dialog import inject
from typing import Any
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog import DialogManager, StartMode
from dishka import FromDishka
from src.adapters.payment.yookassa import create_payment
import asyncio

from src.adapters.database.service import AbstractUserService, AbstractPostService, AbstractPriceService
from src.presentation.states import MyPostsSG, MenuSG
from src.config.reader import Config

@inject
async def on_post_selected(
        callback: CallbackQuery,
        widget: Any,
        dialog_manager: DialogManager,
        item_id: str
):
    dialog_manager.dialog_data["current_index"] = int(item_id)
    await dialog_manager.switch_to(MyPostsSG.view)

@inject
async def back_to_list(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    await dialog_manager.switch_to(MyPostsSG.list)

@inject
async def back_to_main(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    await dialog_manager.start(MenuSG.menu, mode=StartMode.RESET_STACK)


@inject
async def delete_post(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    posts = dialog_manager.dialog_data.get("posts", [])
    current_index = dialog_manager.dialog_data.get("current_index", 0)

    if current_index < len(posts):
        post_id = posts[current_index]['id']
        dialog_manager.dialog_data["post_to_delete"] = post_id
        dialog_manager.dialog_data["post_to_delete_name"] = posts[current_index]['name']

        await dialog_manager.switch_to(MyPostsSG.delete_confirm)


@inject
async def confirm_delete(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager,
        post_service: FromDishka[AbstractPostService]
):
    post_id = dialog_manager.dialog_data.get("post_to_delete")

    if post_id:
        try:
            success = await post_service.delete_post_by_user(post_id)
            if success:
                await callback.answer("Пост удален")
                posts = dialog_manager.dialog_data.get("posts", [])
                current_index = dialog_manager.dialog_data.get("current_index", 0)

                if current_index < len(posts):
                    del posts[current_index]
                    if current_index >= len(posts) and len(posts) > 0:
                        dialog_manager.dialog_data["current_index"] = len(posts) - 1
                    elif len(posts) == 0:
                        dialog_manager.dialog_data["current_index"] = 0
            else:
                await callback.answer("Не удалось удалить пост")
        except Exception as e:
            await callback.answer(f"Ошибка: {str(e)}")

    await dialog_manager.switch_to(MyPostsSG.list)


@inject
async def cancel_delete(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    await dialog_manager.switch_to(MyPostsSG.view)


@inject
async def pay_post(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager,
        config: FromDishka[Config],
        post_service: FromDishka[AbstractPostService],
        price_service: FromDishka[AbstractPriceService]
):
    posts = dialog_manager.dialog_data.get("posts", [])
    current_index = dialog_manager.dialog_data.get("current_index", 0)
    price = await price_service.get_price(name="default")

    if current_index < len(posts):
        post = posts[current_index]
        try:
            payment_url, payment_id = await asyncio.to_thread(
                create_payment,
                post_id=post['id'],
                config=config,
                price=float(price.price)
            )

            await post_service.set_payment_id(post['id'], payment_id)

            await callback.message.answer(
                f"Для оплаты перейдите по ссылке: {payment_url}"
            )
        except Exception as e:
            await callback.message.answer(
                f"Ошибка при создании платежа: {str(e)}"
            )