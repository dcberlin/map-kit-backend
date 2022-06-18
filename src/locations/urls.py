from rest_framework.routers import SimpleRouter
from rest_framework.urls import path

from .views import (
    CategoryViewSet,
    CommunityViewSet,
    LocationViewSet,
    LocationProposalView,
)

router = SimpleRouter()

router.register(r"locations", LocationViewSet)
router.register(r"categories", CategoryViewSet)
router.register(r"communities", CommunityViewSet)


urlpatterns = [
    path("location-proposal/", LocationProposalView.as_view()),
]

urlpatterns += router.urls
