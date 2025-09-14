from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from aiogram_dialog import DialogManager, StartMode

from src.presentation.states import MyPostsSG

router = Router()

@router.message(Command("myposts"))
async def my_posts(
    message: Message,
    dialog_manager: DialogManager
) -> None:
    """
    Start my posts dialog (not admin dialog)
    """
    await dialog_manager.start(
        MyPostsSG.list,
        mode=StartMode.RESET_STACK
    )