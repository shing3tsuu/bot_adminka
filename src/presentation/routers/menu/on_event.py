from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from dishka.integrations.aiogram_dialog import inject
from dishka.integrations.aiogram import FromDishka
from aiogram_dialog.widgets.kbd import Button

from src.presentation.states import PostSG, MyPostsSG
from src.adapters.database.service import AbstractUserService, AbstractPostService, AbstractPriceService

@inject
async def start_create_post(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager,
        user_service: FromDishka[AbstractUserService],
        post_service: FromDishka[AbstractPostService]
):
    current_user = await user_service.get_user_by_tg_id(callback.from_user.id)

    if current_user.is_approved is False:
        info_text = (
            "К сожалению, ваш профиль еще не прошел верификацию.\n"
            "Как только он будет подтвержден, вы сможете создавать посты."
        )
        await callback.message.answer(
            info_text
        )
    else:
        check_posts_value = await post_service.get_unchecked_posts_from_user(callback.from_user.id)
        if check_posts_value is True:
            await dialog_manager.start(PostSG.add_post)
        else:
            info_text = (
                "Одновременное количество постов на модерации не может быть больше трех\n"
                "Дождитесь модерации свои текущих постов, либо удалите один из них для освобождения очереди\n"
            )
            await callback.message.answer(
                info_text
            )

@inject
async def show_my_posts(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    await dialog_manager.start(MyPostsSG.list)

@inject
async def show_info(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    """
    Shows information about the bot (can be changed)
    :param callback:
    :param button:
    :param dialog_manager:
    :return:
    """
    info_text = (
        "ℹ️ Информация о боте:\n\n"
        "Этот бот позволяет создавать и публиковать посты. "
        "Для начала работы нажмите 'Создать пост' и следуйте инструкциям. Канал связи для вопросов и предложений: @moderatormsk"
    )

    await callback.message.answer(
        info_text
    )