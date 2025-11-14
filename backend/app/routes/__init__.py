from .issues import router as issues_router
from .comments import router as comments_router
from .labels import router as labels_router
from .reports import router as reports_router
from .users import router as users_router

__all__ = ["issues_router", "comments_router", "labels_router", "reports_router", "users_router"]
