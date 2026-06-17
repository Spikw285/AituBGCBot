from aiogram import Router

from .game_request import router as game_request_router
from .gm_request import router as gm_request_router
from .ttrpg_signup import router as ttrpg_signup_router

# Главный роутер модуля. При подключении достаточно подключить только его - дочерние подтянутся автоматически.
# IMPORTANT: Периодически обновлять при добавлении нового запроса

router = Router(name="requests")
router.include_router(game_request_router)
router.include_router(gm_request_router)
router.include_router(ttrpg_signup_router)