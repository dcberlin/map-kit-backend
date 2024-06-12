from django.urls import include
from rest_framework.routers import SimpleRouter
from rest_framework.urls import path

from .views import (
    CategoryViewSet,
    CommunityViewSet,
    CommunityAdminViewSet,
    LocationAdminViewSet,
    LocationViewSet,
    LocationProposalView,
    UserView,
)

router = SimpleRouter()

router.register(r"categories", CategoryViewSet)
router.register(r"locations", LocationViewSet)
router.register(r"locations-admin", LocationAdminViewSet, basename="locations-admin")
router.register(r"communities", CommunityViewSet)
router.register(
    r"communities-admin", CommunityAdminViewSet, basename="communities-admin"
)


urlpatterns = [
    path("location-proposal/", LocationProposalView.as_view()),
    path("user/", UserView.as_view()),
]

urlpatterns += router.urls
