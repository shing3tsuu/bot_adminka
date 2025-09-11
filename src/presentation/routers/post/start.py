from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from aiogram_dialog import DialogManager, StartMode

from src.presentation.states import PostSG

router = Router()

@router.message(Command("post"))
async def start_post_creation(
    message: Message,
    dialog_manager: DialogManager
) -> None:
    await dialog_manager.start(
        PostSG.menu,
        mode=StartMode.RESET_STACK
    )