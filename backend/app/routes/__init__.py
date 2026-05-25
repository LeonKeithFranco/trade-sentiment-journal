from app.domains.auth.route import router as auth_router
from app.domains.trade.route import router as trade_router

routers = [auth_router, trade_router]

__all__ = ["routers"]
