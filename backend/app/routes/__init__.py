from app.domains.auth.route import router as auth_router
from app.domains.journal_entries.route import router as journal_entries_router
from app.domains.nlp.route import router as nlp_router
from app.domains.trades.route import router as trades_router

routers = [
    auth_router,
    trades_router,
    journal_entries_router,
    nlp_router,
]

__all__ = ["routers"]
