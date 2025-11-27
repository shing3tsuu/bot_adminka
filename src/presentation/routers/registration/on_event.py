import re
from typing import Any
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, StartMode
from dishka.integrations.aiogram_dialog import inject
from dishka.integrations.aiogram import FromDishka
from aiogram_dialog.widgets.kbd import Button

from src.adapters.database.service import AbstractUserService, AbstractPostService, AbstractPriceService
from src.adapters.database.dto import UserRequestDTO
from src.presentation.states import RegistrationSG, MenuSG


def validate_phone(phone: str) -> bool:
    """
    Validate phone number using re module.
    :param phone:
    :return:
    """
    cleaned_phone = re.sub(r'\D', '', phone)

    if len(cleaned_phone) not in [10, 11]:
        return False

    if len(cleaned_phone) == 11 and not cleaned_phone.startswith(('7', '8')):
        return False

    return True


def format_phone(phone: str) -> str:
    """
    Format phone number. Replace starting 8 with 7.
    :param phone:
    :return:
    """
    cleaned_phone = re.sub(r'\D', '', phone)

    # Заменяем начальную 8 на 7
    if cleaned_phone.startswith('8'):
        cleaned_phone = '7' + cleaned_phone[1:]

    if len(cleaned_phone) == 10:
        cleaned_phone = '7' + cleaned_phone

    if len(cleaned_phone) == 11:
        return f"+{cleaned_phone[0]} ({cleaned_phone[1:4]}) {cleaned_phone[4:7]}-{cleaned_phone[7:9]}-{cleaned_phone[9:]}"

    return cleaned_phone

@inject
async def on_surname_entered(
        message: Message,
        widget: Any,
        dialog_manager: DialogManager,
        text: str
):
    if len(text) < 2 or len(text) > 30:
        await message.answer("Фамилия должна содержать от 2 до 30 символов.")
        return

    dialog_manager.dialog_data["surname"] = text.title()
    await dialog_manager.next()

@inject
async def on_name_entered(
        message: Message,
        widget: Any,
        dialog_manager: DialogManager,
        text: str
):
    if len(text) < 2 or len(text) > 30:
        await message.answer("Имя должно содержать от 2 до 30 символов.")
        return

    dialog_manager.dialog_data["name"] = text.title()
    await dialog_manager.next()

@inject
async def on_patronymic_entered(
        message: Message,
        widget: Any,
        dialog_manager: DialogManager,
        text: str
):
    if text and (len(text) < 2 or len(text) > 30):
        await message.answer("Отчество должно содержать от 2 до 30 символов.")
        return

    dialog_manager.dialog_data["patronymic"] = text.title() if text else None
    await dialog_manager.next()

@inject
async def on_phone_entered(
        message: Message,
        widget: Any,
        dialog_manager: DialogManager,
        text: str
):
    if not validate_phone(text):
        await message.answer("Пожалуйста, введите корректный номер телефона.")
        return

    dialog_manager.dialog_data["phone"] = format_phone(text)
    await dialog_manager.next()

@inject
async def on_organization_entered(
        message: Message,
        widget: Any,
        dialog_manager: DialogManager,
        text: str
):
    if len(text) < 2 or len(text) > 100:
        await message.answer("Название организации должно содержать от 2 до 100 символов.")
        return

    dialog_manager.dialog_data["organization"] = text
    await dialog_manager.next()

@inject
async def on_cancel(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager
):
    await dialog_manager.start(MainSG.menu, mode=StartMode.RESET_STACK)

@inject
async def on_confirm(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager,
        user_service: FromDishka[AbstractUserService]
):
    data = dialog_manager.dialog_data

    user = await user_service.get_current_user()

    updated_user = await user_service.change_user_data(
        UserRequestDTO(
            tg_id=user.tg_id,
            tg_username=user.tg_username,
            surname=data["surname"],
            name=data["name"],
            patronymic=data["patronymic"],
            number=data["phone"],
            organization=data["organization"],
            is_admin=user.is_admin,
            is_approved=user.is_approved
        )
    )

    await callback.message.answer(
        "✅ Регистрация завершена!"
    )
    await dialog_manager.start(MenuSG.menu, mode=StartMode.RESET_STACK)