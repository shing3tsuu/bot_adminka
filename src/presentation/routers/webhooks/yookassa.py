from fastapi import APIRouter, HTTPException
from yookassa import Webhook
from dishka.integrations.fastapi import DishkaRoute
from dishka import FromDishka
from dishka.integrations.fastapi import inject

from src.adapters.database.service import PostService

router = APIRouter(route_class=DishkaRoute)

@router.post("/webhook/yookassa")
@inject
async def yookassa_webhook(
        update: dict,
        post_service: FromDishka[PostService]
):
    try:
        event = Webhook.parse(update)

        if event.event == 'payment.succeeded':
            post_id = event.object.metadata.get('post_id')
            if post_id:
                await post_service.update_post(post_id, is_paid=True)

        return {"status": "ok"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))