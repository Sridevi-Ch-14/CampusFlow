from fastapi import APIRouter
from app.api.v1 import (
    auth,
    users,
    complaints,
    categories,
    locations,
    comments,
    attachments,
    notifications,
    ratings,
    analytics,
    sla
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(complaints.router)
api_router.include_router(categories.router)
api_router.include_router(locations.router)
api_router.include_router(comments.router)
api_router.include_router(attachments.router)
api_router.include_router(notifications.router)
api_router.include_router(ratings.router)
api_router.include_router(analytics.router)
api_router.include_router(sla.router)
