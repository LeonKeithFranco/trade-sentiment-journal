from app.domains.auth.route import router as auth_router
from app.domains.journal_entries.route import router as jounal_entries_router
from app.domains.trades.route import router as trades_router

routers = [auth_router, trades_router, jounal_entries_router]

__all__ = ["routers"]
