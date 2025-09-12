from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from aiogram_dialog import DialogManager, StartMode
from dishka import FromDishka

from src.adapters.database.service import UserService
from src.presentation.states import MenuSG

router = Router()

@router.message(Command("menu"))
async def menu(
    message: Message,
    dialog_manager: DialogManager,
    users: FromDishka[UserService]
) -> None:
    """
    Main menu command
    if user is not registered return to registration
    """

    current_user = await users.get_user_by_tg_id(message.from_user.id)

    if not current_user or not current_user.name:
        await dialog_manager.start(
            RegistrationSG.surname,
            mode=StartMode.RESET_STACK
        )
    else:
        await dialog_manager.start(
            MenuSG.menu,
            mode=StartMode.RESET_STACK
        )