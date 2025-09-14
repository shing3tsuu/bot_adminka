from typing import Any
from aiogram_dialog import DialogManager

async def get_registration_data(dialog_manager: DialogManager, **kwargs) -> dict[str, Any]:
    data = dialog_manager.dialog_data

    return {
        "surname": data.get("surname", "не указано"),
        "name": data.get("name", "не указано"),
        "patronymic": data.get("patronymic", "не указано"),
        "phone": data.get("phone", "не указано")
    }