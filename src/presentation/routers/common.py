from aiogram import Router

from src.presentation.routers.menu.start import router as menu_start_router
from src.presentation.routers.menu.dialog import dialog as menu_dialog_router

from src.presentation.routers.registration.start import router as registration_start_router
from src.presentation.routers.registration.dialog import dialog as registration_dialog_router

from src.presentation.routers.createpost.start import router as create_post_start_router
from src.presentation.routers.createpost.dialog import dialog as create_post_dialog_router

from src.presentation.routers.myposts.start import router as my_posts_start_router
from src.presentation.routers.myposts.dialog import dialog as my_posts_dialog_router

from src.presentation.routers.admin.start import router as admin_start_router
from src.presentation.routers.admin.dialog import dialog as admin_dialog_router

common_router = Router()

common_router.include_routers(
    registration_start_router,
    menu_start_router,
    create_post_start_router,
    my_posts_start_router,
    admin_start_router,
    registration_dialog_router,
    menu_dialog_router,
    create_post_dialog_router,
    my_posts_dialog_router,
    admin_dialog_router,
)
