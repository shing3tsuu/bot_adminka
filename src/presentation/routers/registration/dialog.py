from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Back, Next, Cancel, Button, Group
from aiogram_dialog.widgets.input import TextInput, MessageInput

from src.presentation.states import RegistrationSG
from . import getter, on_event

dialog = Dialog(
    Window(
        Const("📝 Регистрация\n\nВведите вашу фамилию:"),
        TextInput(
            id="surname_input",
            type_factory=str,
            on_success=on_event.on_surname_entered
        ),
        Cancel(Const("❌ Отмена")),
        state=RegistrationSG.surname,
        getter=getter.get_registration_data
    ),
    Window(
        Const("Теперь введите ваше имя:"),
        TextInput(
            id="name_input",
            type_factory=str,
            on_success=on_event.on_name_entered
        ),
        Back(Const("◀️ Назад")),
        Cancel(Const("❌ Отмена")),
        state=RegistrationSG.name,
        getter=getter.get_registration_data
    ),
    Window(
        Const("Введите ваше отчество:"),
        TextInput(
            id="patronymic_input",
            type_factory=str,
            on_success=on_event.on_patronymic_entered
        ),
        Back(Const("◀️ Назад")),
        Cancel(Const("❌ Отмена")),
        state=RegistrationSG.patronymic,
        getter=getter.get_registration_data
    ),
    Window(
        Const("Введите ваш номер телефона:"),
        TextInput(
            id="phone_input",
            type_factory=str,
            on_success=on_event.on_phone_entered
        ),
        Back(Const("◀️ Назад")),
        Cancel(Const("❌ Отмена")),
        state=RegistrationSG.phone,
        getter=getter.get_registration_data
    ),
    Window(
        Format("✅ Проверьте введенные данные:\n\n"
               "Фамилия: {surname}\n"
               "Имя: {name}\n"
               "Отчество: {patronymic}\n"
               "Телефон: {phone}\n\n"
               "Все верно?"),
        Group(
            Button(Const("✅ Подтвердить"), id="confirm", on_click=on_event.on_confirm),
            Back(Const("◀️ Исправить")),
            Cancel(Const("❌ Отмена")),
        ),
        state=RegistrationSG.confirm,
        getter=getter.get_registration_data
    )
)
