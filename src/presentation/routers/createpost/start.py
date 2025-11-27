from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from aiogram_dialog import DialogManager, StartMode
from dishka import FromDishka

from src.adapters.database.service import AbstractUserService, AbstractPostService, AbstractPriceService
from src.presentation.states import PostSG, RegistrationSG

router = Router()

@router.message(Command("post"))
async def start_post_creation(
    message: Message,
    dialog_manager: DialogManager,
    user_service: FromDishka[AbstractUserService]
) -> None:
    """
    Command for starting post creation
    if user is not registered return to registration
    """

    current_user = await user_service.get_user_by_tg_id(message.from_user.id)

    if not current_user or not current_user.name:
        await dialog_manager.start(
            RegistrationSG.surname,
            mode=StartMode.RESET_STACK
        )
    else:
        await dialog_manager.start(
            PostSG.menu,
            mode=StartMode.RESET_STACK
        )