from django.urls import path
from app.api.viewsets.interaction import (
    CreateInteraction,
    RecentInteractions,
    TopContacts,
    SpamAggregation,
)

urlpatterns = [
    path("interactions/", CreateInteraction.as_view(), name="create-interaction"),
    path("interactions/recent/", RecentInteractions.as_view(), name="recent-interactions"),
    path("interactions/top/", TopContacts.as_view(), name="top-contacts"),
    path("interactions/spam-aggregate/", SpamAggregation.as_view(), name="spam-aggregation"),
]