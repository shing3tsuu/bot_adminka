from typing import Any
from aiogram_dialog import DialogManager
from dishka.integrations.aiogram import FromDishka
from dishka.integrations.aiogram_dialog import inject
from dishka import FromDishka
from aiogram.types import ContentType
from aiogram_dialog.api.entities import MediaAttachment, MediaId

from src.adapters.database.service import AbstractUserService, AbstractPostService, AbstractPriceService
from src.config.reader import Config


@inject
async def get_users_list(
        dialog_manager: DialogManager,
        user_service: FromDishka[AbstractUserService],
        **kwargs
) -> dict[str, Any]:
    users = await user_service.get_unapproved_users()

    users_dicts = []
    for user in users:
        user_dict = {
            'id': user.id,
            'name': f"{user.surname or ''} {user.name or ''}".strip() or "Без имени",
            'tg_id': user.tg_id,
            'number': user.number or "Не указан",
            'is_admin': user.is_admin,
            'is_approved': user.is_approved
        }
        users_dicts.append(user_dict)

    dialog_manager.dialog_data["users"] = users_dicts

    if not users_dicts:
        return {
            "users_list": "Нет пользователей.",
            "users": []
        }

    users_list_items = [f"• {user_dict['name']} ({'✅' if user_dict['is_approved'] else '❌'})"
                        for user_dict in users_dicts]
    users_list = "\n".join(users_list_items)

    return {
        "users_list": f"Всего пользователей: {len(users_dicts)}\n\n{users_list}",
        "users": [{"id": i, "name": f"{user_dict['name']} ({'✅' if user_dict['is_approved'] else '❌'})"}
                  for i, user_dict in enumerate(users_dicts)]
    }

@inject
async def get_user_details(
        dialog_manager: DialogManager,
        **kwargs
) -> dict[str, Any]:
    users = dialog_manager.dialog_data.get("users", [])
    current_index = dialog_manager.dialog_data.get("current_user_index", 0)

    if not users or current_index >= len(users):
        return {
            "user_name": "Пользователь не найден",
            "user_username": "Неизвестно",
            "user_id": "Неизвестно",
            "user_phone": "Неизвестно",
            "user_status": "Неизвестно",
            "is_admin": "Неизвестно",
            "is_approved": "Неизвестно",
            "not_approved": False,
            "is_approved_flag": False
        }

    user = users[current_index]

    return {
        "user_name": user['name'],
        "user_id": user['tg_id'],
        "user_phone": user['number'],
        "user_status": "Администратор" if user['is_admin'] else "Пользователь",
        "is_admin": "Да" if user['is_admin'] else "Нет",
        "is_approved": "Да" if user['is_approved'] else "Нет",
        "not_approved": not user['is_approved'],
        "is_approved_flag": user['is_approved']
    }

@inject
async def get_current_price(
        dialog_manager: DialogManager,
        price_service: FromDishka[AbstractPriceService],
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
        user_service: FromDishka[AbstractUserService],
        post_service: FromDishka[AbstractPostService],
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
        "posts": [{"id": i, "name": f"{post_dict['name']}"} for
                  i, post_dict in enumerate(posts_dicts)]
    }


@inject
async def get_post_details(
        dialog_manager: DialogManager,
        user_service: FromDishka[AbstractUserService],
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
    elif post.get('media_type') == 'video':
        media = MediaAttachment(ContentType.VIDEO, path=post_media)
    else:
        media = None

    return {
        "post_name": post['name'],
        "post_text": post['text'],
        "sender_name": sender_name,
        "sender_phone": sender_phone,
        "post_status": "На модерации",
        "has_media": bool(post['media_link']),
        "media": media,
    }

@inject
async def get_all_users_list(
        dialog_manager: DialogManager,
        user_service: FromDishka[AbstractUserService],
        post_service: FromDishka[AbstractPostService],
        **kwargs
) -> dict[str, Any]:
    page = dialog_manager.dialog_data.get("all_users_page", 0)
    users_per_page = 5

    all_users = await user_service.get_all_users()

    all_users.sort(key=lambda u: u.id)

    total_pages = (len(all_users) + users_per_page - 1) // users_per_page
    start_idx = page * users_per_page
    end_idx = start_idx + users_per_page
    users_page = all_users[start_idx:end_idx]

    users_with_posts = []
    for user in users_page:
        user_posts = await post_service.get_published_posts(user.id)
        users_with_posts.append({
            'user': user,
            'posts_count': len(user_posts)
        })

    users_dicts = []
    for user_data in users_with_posts:
        user = user_data['user']
        posts_count = user_data['posts_count']

        user_dict = {
            'id': user.id,
            'name': f"{user.surname or ''} {user.name or ''} {user.patronymic or ''}".strip() or "Без имени",
            'tg_id': user.tg_id,
            'tg_username': user.tg_username or "Не указан",
            'number': user.number or "Не указан",
            'is_admin': user.is_admin,
            'is_approved': user.is_approved,
            'posts_count': posts_count
        }
        users_dicts.append(user_dict)

    dialog_manager.dialog_data["all_users"] = users_dicts
    dialog_manager.dialog_data["all_users_total_pages"] = total_pages
    dialog_manager.dialog_data["all_users_current_page"] = page

    if not users_dicts:
        return {
            "all_users_list": "Нет пользователей.",
            "all_users": [],
            "current_page": page + 1,
            "total_pages": total_pages,
            "has_previous": page > 0,
            "has_next": page < total_pages - 1
        }

    users_list_items = []
    for user_dict in users_dicts:
        status = "✅" if user_dict['is_approved'] else "❌"
        admin = "👑" if user_dict['is_admin'] else "👤"
        posts_info = f"📝 {user_dict['posts_count']} пост."
        users_list_items.append(f"• {admin} {user_dict['name']} {status} {posts_info}")

    users_list = "\n".join(users_list_items)

    return {
        "all_users_list": f"Страница {page + 1} из {total_pages}\n\n{users_list}",
        "all_users": [{"id": i, "name": f"{user_dict['name']} ({user_dict['posts_count']} пост.)"}
                      for i, user_dict in enumerate(users_dicts)],
        "current_page": page + 1,
        "total_pages": total_pages,
        "has_previous": page > 0,
        "has_next": page < total_pages - 1
    }


@inject
async def get_all_user_details(
        dialog_manager: DialogManager,
        user_service: FromDishka[AbstractUserService],
        post_service: FromDishka[AbstractPostService],
        **kwargs
) -> dict[str, Any]:
    current_index = dialog_manager.dialog_data.get("all_users_current_index")
    searched_index = dialog_manager.dialog_data.get("searched_user_index")

    if searched_index is not None:
        all_users = dialog_manager.dialog_data.get("searched_users", [])
        current_index = searched_index
        source = "search"
    else:
        all_users = dialog_manager.dialog_data.get("all_users", [])
        current_index = current_index or 0
        source = "normal"

    if not all_users or current_index >= len(all_users):
        return {
            "user_name": "Пользователь не найден",
            "user_tg_username": "Неизвестно",
            "user_tg_id": "Неизвестно",
            "user_phone": "Неизвестно",
            "user_status": "Неизвестно",
            "is_admin": "Неизвестно",
            "is_approved": "Неизвестно",
            "posts_count": 0,
            "posts_info": ""
        }

    user_data = all_users[current_index]

    dialog_manager.dialog_data["current_detail_source"] = source

    user_posts = await post_service.get_published_posts(user_data['id'])

    published_posts = [p for p in user_posts if p.is_published]
    unpaid_posts = [p for p in user_posts if not p.is_paid]
    pending_posts = [p for p in user_posts if not p.is_checked]

    posts_info_lines = [
        f"Всего постов: {len(user_posts)}",
        f"Опубликовано: {len(published_posts)}",
        f"Неоплаченных: {len(unpaid_posts)}",
        f"На модерации: {len(pending_posts)}"
    ]

    if user_posts:
        posts_info_lines.append("\nПоследние посты:")
        for i, post in enumerate(user_posts[:3], 1):
            status = "✅" if post.is_published else "⏳" if post.is_checked else "🕒"
            paid = "💳" if post.is_paid else "❌"
            posts_info_lines.append(f"{i}. {post.name} {status}{paid}")

    return {
        "user_name": user_data['name'],
        "user_tg_username": f"@{user_data['tg_username']}" if user_data['tg_username'] else "Не указан",
        "user_tg_id": user_data['tg_id'],
        "user_phone": user_data['number'],
        "user_status": "Администратор" if user_data['is_admin'] else "Пользователь",
        "is_admin": "Да" if user_data['is_admin'] else "Нет",
        "is_approved": "Да" if user_data['is_approved'] else "Нет",
        "posts_count": user_data['posts_count'],
        "posts_info": "\n".join(posts_info_lines)
    }


@inject
async def get_search_results(
        dialog_manager: DialogManager,
        user_service: FromDishka[AbstractUserService],
        post_service: FromDishka[AbstractPostService],
        **kwargs
) -> dict[str, Any]:
    search_query = dialog_manager.dialog_data.get("search_query", "")

    if not search_query:
        return {
            "search_results_list": "Введите поисковый запрос.",
            "search_results": []
        }

    users = await user_service.search_users_by_fio(search_query)

    users_with_posts = []
    for user in users:
        user_posts = await post_service.get_published_posts(user.id)
        users_with_posts.append({
            'user': user,
            'posts_count': len(user_posts)
        })

    users_dicts = []
    for user_data in users_with_posts:
        user = user_data['user']
        posts_count = user_data['posts_count']

        user_dict = {
            'id': user.id,
            'name': f"{user.surname or ''} {user.name or ''}".strip() or "Без имени",
            'tg_id': user.tg_id,
            'tg_username': user.tg_username or "Не указан",
            'number': user.number or "Не указан",
            'is_admin': user.is_admin,
            'is_approved': user.is_approved,
            'posts_count': posts_count
        }
        users_dicts.append(user_dict)

    dialog_manager.dialog_data["searched_users"] = users_dicts

    if not users_dicts:
        return {
            "search_results_list": f"По запросу '{search_query}' ничего не найдено.",
            "search_results": [],
            "search_query": search_query
        }

    users_list_items = []
    for user_dict in users_dicts:
        status = "✅" if user_dict['is_approved'] else "❌"
        admin = "👑" if user_dict['is_admin'] else "👤"
        posts_info = f"📝 {user_dict['posts_count']} пост."
        users_list_items.append(f"• {admin} {user_dict['name']} {status} {posts_info}")

    users_list = "\n".join(users_list_items)

    return {
        "search_results_list": f"Результаты поиска по '{search_query}':\n\n{users_list}",
        "search_results": [{"id": i, "name": f"{user_dict['name']} ({user_dict['posts_count']} пост.)"}
                           for i, user_dict in enumerate(users_dicts)],
        "search_query": search_query
    }