from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram_dialog import DialogManager, StartMode
from dishka.integrations.aiogram import FromDishka

from src.adapters.database.service import UserService
from src.presentation.states import AdminSG

router = Router()

@router.message(F.text == "Администрирование")
async def admin_panel(
    message: Message,
    dialog_manager: DialogManager,
    user_service: FromDishka[UserService]
) -> None:
    user = await user_service.get_current_user()
    if not user.is_admin:
        await message.answer("У вас нет прав для доступа к этой команде.")
        return

    await dialog_manager.start(AdminSG.moderation_list, mode=StartMode.RESET_STACK)