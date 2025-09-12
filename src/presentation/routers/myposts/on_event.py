from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from dishka.integrations.aiogram_dialog import inject
from typing import Any
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog import DialogManager, StartMode

from src.presentation.states import MyPostsSG, MenuSG

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