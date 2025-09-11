from dishka import FromDishka
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from aiogram_dialog import DialogManager, StartMode

from src.adapters.database.service import UserService
from src.adapters.database.dto import UserRequestDTO
from src.presentation.states import RegistrationSG
from src.config.reader import Config

router = Router()

@router.message(Command("start"))
async def start(
        message: Message,
        command: CommandObject,
        users: FromDishka[UserService],
        dialog_manager: DialogManager,
        config: FromDishka[Config]
) -> None:
    await message.answer(
        "Добро пожаловать!"
    )

    current_user = await users.get_user_by_tg_id(message.from_user.id)

    if not current_user:
        if message.from_user.id in config.bot.admin_ids:
            is_admin = True
        else:
            is_admin = False

        await users.add_user(
            UserRequestDTO(
                tg_id=message.from_user.id,
                tg_username=message.from_user.username,
                surname=None,
                name=None,
                patronymic=None,
                number=None,
                is_admin=is_admin
            )
        )
        await message.answer(
            "И привет, новенький!"
        )

    if current_user.name is None:
        await message.answer(
            "Кажется вы не зарегестрированы, давайте сделаем это!"
        )

        await dialog_manager.start(
            RegistrationSG.surname,
            mode=StartMode.RESET_STACK
        )

        return
