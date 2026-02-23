from aiogram import Router

from .start import router as start_router
from .game import router as game_router
from .deposit import router as deposit_router
from .withdraw import router as withdraw_router
from .profile import router as profile_router
from .support import router as support_router
from .admin import router as admin_router
from .coupon import router as coupon_router

def get_main_router() -> Router:
    router = Router()
    router.include_router(start_router, name="start")
    router.include_router(coupon_router, name="coupon")
    router.include_router(game_router, name="game")
    router.include_router(deposit_router, name="deposit")
    router.include_router(withdraw_router, name="withdraw")
    router.include_router(profile_router, name="profile")
    router.include_router(support_router, name="support")
    router.include_router(admin_router, name="admin")
    return router
