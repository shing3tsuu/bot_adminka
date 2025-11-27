from dishka import FromDishka
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from aiogram_dialog import DialogManager, StartMode
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from src.adapters.database.service import AbstractUserService, AbstractPostService, AbstractPriceService
from src.adapters.database.dto import UserRequestDTO, UserDTO
from src.presentation.states import RegistrationSG, MenuSG
from src.config.reader import Config

router = Router()

@router.message(Command("start"))
async def start(
        message: Message,
        command: CommandObject,
        user_service: FromDishka[AbstractUserService],
        dialog_manager: DialogManager,
        config: FromDishka[Config]
) -> None:
    """
    Main menu command
    if user first time in bot saving his (tg_id, tg_username, is_admin)
    if user dont have surname in database he will be redirected to registration
    if user already registered he will be redirected to main menu
    """
    admin_kb = []

    current_user = await user_service.get_user_by_tg_id(message.from_user.id)

    if message.from_user.id in config.bot.admin_ids or current_user and current_user.is_admin: admin_kb = [[KeyboardButton(text="Администрирование")]]

    keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Меню")],*admin_kb,], resize_keyboard=True)

    await message.answer(
        "Привет",
        reply_markup=keyboard
    )

    if not current_user:
        # If the user is not in the database, he is automatically entered with basic parameters, and then goes to the registration menu
        if message.from_user.id in config.bot.admin_ids:
            is_admin = True
            is_approved = True
        else:
            is_admin = False
            is_approved = False

        await user_service.add_user(
            UserRequestDTO(
                tg_id=message.from_user.id,
                tg_username=message.from_user.username,
                surname=None,
                name=None,
                patronymic=None,
                number=None,
                is_admin=is_admin,
                is_approved=is_approved
            )
        )
        await message.answer(
            "Похоже ты новенький!\nДавай пройдем регистрацию, что бы ты мог отправлять свои посты!",
        )

        await dialog_manager.start(
            RegistrationSG.surname,
            mode=StartMode.RESET_STACK
        )
        return

    else:
        if current_user.name is not None:
            # If the user already exists in the database and is registered, he/she immediately goes to the main menu
            await dialog_manager.start(
                MenuSG.menu,
                mode=StartMode.RESET_STACK
            )
            return

        else:
            # If the user already exists in the database but is not registered, he goes to the registration menu
            await message.answer(
                "Давай пройдем регистрацию, что бы ты мог отправлять свои посты!"
            )

            await dialog_manager.start(
                RegistrationSG.surname,
                mode=StartMode.RESET_STACK
            )
            return
