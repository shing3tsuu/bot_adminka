from typing import Any
from aiogram_dialog import DialogManager
from dishka.integrations.aiogram import FromDishka
from dishka.integrations.aiogram_dialog import inject

from src.adapters.database.service import PostService, UserService

@inject
async def get_preview_data(dialog_manager: DialogManager, **kwargs) -> dict[str, Any]:
    post_data = dialog_manager.dialog_data
    media_status = "Не приложено"
    if post_data.get("media_url"):
        media_type = post_data.get("media_type", "photo")
        media_status = "Фото" if media_type == "photo" else "Видео"

    return {
        "name": post_data.get("name", ""),
        "text": post_data.get("text", ""),
        "media_status": media_status
    }