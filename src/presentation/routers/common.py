from aiogram import Router

from src.presentation.routers.post.start import router as post_start_router
from src.presentation.routers.post.dialog import dialog as post_dialog_router

from src.presentation.routers.registration.start import router as registration_start_router
from src.presentation.routers.registration.dialog import dialog as registration_dialog_router

common_router = Router()

common_router.include_routers(
    post_start_router,
    post_dialog_router,
    registration_start_router,
    registration_dialog_router,
)