from typing import Any
from aiogram_dialog import DialogManager
from dishka.integrations.aiogram import FromDishka
from dishka.integrations.aiogram_dialog import inject
from dishka import FromDishka
from aiogram.types import ContentType
from aiogram_dialog.api.entities import MediaAttachment, MediaId

from src.adapters.database.service import PostService, UserService, PriceService
from src.config.reader import Config

@inject
async def get_current_price(
        dialog_manager: DialogManager,
        price_service: FromDishka[PriceService],
        **kwargs
) -> dict[str, Any]:

    price = await price_service.get_price("default")
    if not price:
        price = await price_service.add_price("default", 100)
    return {
        "current_price": price.price if price else "Не установлена"
    }

@inject
async def get_posts_list(
        dialog_manager: DialogManager,
        post_service: FromDishka[PostService],
        user_service: FromDishka[UserService],
        **kwargs
) -> dict[str, Any]:
    posts = await post_service.get_unchecked_posts()

    # Convert PostDTOs to Dictionaries for Serialization
    posts_dicts = []
    for post in posts:
        post_dict = {
            'id': post.id,
            'name': post.name,
            'text': post.text,
            'media_link': post.media_link,
            'media_type': post.media_type,
            'is_publish_now': post.is_publish_now,
            'publish_date': post.publish_date.isoformat() if post.publish_date else None,
            'is_checked': post.is_checked,
            "is_paid": post.is_paid,
            'sender_id': post.sender_id
        }
        posts_dicts.append(post_dict)

    dialog_manager.dialog_data["posts"] = posts_dicts

    if not posts_dicts:
        return {
            "posts_list": "Нет постов на модерации.",
            "posts": []
        }

    posts_list_items = [f"• {post_dict['name']}" for post_dict in
                        posts_dicts]
    posts_list = "\n".join(posts_list_items)

    user = await user_service.get_user_by_id(posts_dicts[0]['sender_id'])

    return {
        "posts_list": f"Всего на модерации: {len(posts_dicts)}\n\n{posts_list}",
        "posts": [{"id": i, "name": f"{post_dict['name']} ({user.surname} {user.name})"} for
                  i, post_dict in enumerate(posts_dicts)]
    }


@inject
async def get_post_details(
        dialog_manager: DialogManager,
        user_service: FromDishka[UserService],
        config: FromDishka[Config],
        **kwargs
) -> dict[str, Any]:
    posts = dialog_manager.dialog_data.get("posts", [])
    current_index = dialog_manager.dialog_data.get("current_index", 0)

    if not posts or current_index >= len(posts):
        return {
            "post_name": "Пост не найден",
            "post_text": "",
            "sender_name": "Неизвестно",
            "sender_phone": "Неизвестно",
            "post_status": "Неизвестно",
            "has_media": False,
            "post_media": ""
        }

    # Ensure we're working with a dictionary, not a PostDTO object
    post = dict(posts[current_index]) if hasattr(posts[current_index], '_asdict') else posts[current_index]

    sender = await user_service.get_user_by_id(post['sender_id'])
    sender_name = f"{sender.surname} {sender.name} {sender.patronymic}" if sender else "Неизвестно"
    sender_phone = sender.number if sender else "Неизвестно"


    post_media = ""

    if post.get('media_link'):
        # If this is a file_id from Telegram (starts with AgA)
        if post['media_link'].startswith('AgA'):
            post_media = post['media_link']
        else:
            # If it's a file path, form the full URL using proper concatenation
            # Make sure media_url ends with / and path doesn't start with /
            media_url = config.media.media_url.rstrip('/') + '/'
            media_path = post['media_link'].lstrip('/')

            # Using urljoin to form URLs correctly
            post_media = media_path

    if post.get('media_type') == 'photo':
        media = MediaAttachment(ContentType.PHOTO, path=post_media)
    elif post.get('media_type') == None:
        media = None
    else:
        media = MediaAttachment(ContentType.VIDEO, path=post_media)

    return {
        "post_name": post['name'],
        "post_text": post['text'],
        "sender_name": sender_name,
        "sender_phone": sender_phone,
        "post_status": "На модерации",
        "has_media": bool(post['media_link']),
        "media": media,
    }
