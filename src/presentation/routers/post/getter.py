from typing import Any
from aiogram_dialog import DialogManager
from dishka.integrations.aiogram import FromDishka
from dishka.integrations.aiogram_dialog import inject

from src.adapters.database.service import PostService, UserService

@inject
async def get_post_data(dialog_manager: DialogManager, **kwargs) -> dict[str, Any]:
    return {
        "post_data": dialog_manager.dialog_data
    }