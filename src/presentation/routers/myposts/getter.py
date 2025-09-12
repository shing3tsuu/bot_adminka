from typing import Any
from aiogram_dialog import DialogManager
from dishka.integrations.aiogram import FromDishka
from dishka.integrations.aiogram_dialog import inject
from datetime import datetime
import os
from urllib.parse import urljoin

from src.adapters.database.service import PostService, UserService
from src.config.reader import Config


@inject
async def get_posts_list(
        dialog_manager: DialogManager,
        post_service: FromDishka[PostService],
        user_service: FromDishka[UserService],
        **kwargs
) -> dict[str, Any]:
    """
    This function is used to get the list of posts for the user.
    """
    user = await user_service.get_current_user()
    posts = await post_service.get_posts(user.id)

    # Convert PostDTOs to Dictionaries for Serialization
    posts_dicts = []
    for post in posts:
        post_dict = {
            'id': post.id,
            'name': post.name,
            'text': post.text,
            'image_link': post.image_link,
            'is_publish_now': post.is_publish_now,
            'publish_date': post.publish_date.isoformat() if post.publish_date else None,
            'is_checked': post.is_checked,
            'sender_id': post.sender_id
        }
        posts_dicts.append(post_dict)

    dialog_manager.dialog_data["posts"] = posts_dicts
    dialog_manager.dialog_data["current_index"] = 0

    if not posts_dicts:
        return {
            "posts_list": "У вас пока нет созданных постов.",
            "posts": []
        }

    # We form a list of posts taking into account new statuses
    posts_list_items = []
    for post_dict in posts_dicts:
        if post_dict['is_checked']:
            if post_dict['is_publish_now']:
                status = "✅ Опубликован"
            else:
                status = "⏳ Ожидает публикации"
        else:
            status = "⏳ На проверке"

        posts_list_items.append(f"• {post_dict['name']} ({status})")

    posts_list = "\n".join(posts_list_items)

    return {
        "posts_list": f"Всего постов: {len(posts_dicts)}\n\n{posts_list}",
        "posts": [{"id": i, "name": f"{post_dict['name']} ({status})"} for i, (post_dict, status) in
                  enumerate(zip(posts_dicts, posts_list_items))]
    }

@inject
async def get_post_details(
        dialog_manager: DialogManager,
        config: FromDishka[Config],
        **kwargs
) -> dict[str, Any]:
    """
    This function is used to get the details of a post (On user click).
    """
    posts = dialog_manager.dialog_data.get("posts", [])
    current_index = dialog_manager.dialog_data.get("current_index", 0)

    if not posts or current_index >= len(posts):
        return {
            "post_name": "Пост не найден",
            "post_text": "",
            "has_image": False,
            "post_status": "Неизвестно",
            "publish_date": "",
            "post_image": ""
        }

    post = posts[current_index]

    # Determine the status of the post
    if post['is_checked']:
        if post['is_publish_now']:
            status = "✅ Опубликован"
        else:
            status = "⏳ Ожидает публикации"
    else:
        status = "⏳ На проверке"

    # Format the publication date
    publish_date = ""
    if post.get('publish_date'):
        try:
            if isinstance(post['publish_date'], str):
                publish_date_obj = datetime.fromisoformat(post['publish_date'])
                publish_date = publish_date_obj.strftime("%d.%m.%Y %H:%M")
        except (ValueError, TypeError):
            publish_date = ""

    # Form the full path to the image
    post_image = ""
    has_image = False

    if post.get('image_link'):
        # If this is a file_id from Telegram (starts with AgA)
        if post['image_link'].startswith('AgA'):
            post_image = post['image_link']
            has_image = True
        else:
            # If it's a file path, form the full URL using proper concatenation
            # Make sure media_url ends with / and path doesn't start with /
            media_url = config.media.media_url.rstrip('/') + '/'
            image_path = post['image_link'].lstrip('/')

            # Using urljoin to form URLs correctly
            post_image = image_path
            has_image = True

    return {
        "post_name": post.get('name', ''),
        "post_text": post.get('text', ''),
        "has_image": has_image,
        "post_image": post_image,
        "post_status": status,
        "publish_date": f"Дата публикации: {publish_date}" if publish_date else "Дата публикации не установлена",
        "current_index": current_index,
        "total_posts": len(posts)
    }