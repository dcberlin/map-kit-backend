from django_filters import rest_framework as filters
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    AllowAny,
)
from django.contrib.postgres.search import SearchVector
from rest_framework import generics, viewsets
from rest_framework_gis.filters import InBBoxFilter

from .models import Category, Community, Location
from .serializers import (
    CategorySerializer,
    CommunitySerializer,
    LocationProposalSerializer,
    LocationSerializer,
)
from .permissions import IsApprovedUser, IsApprovedUserOrReadOnly


"""
ViewSets
"""


class LocationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsApprovedUserOrReadOnly]
    queryset = Location.objects.filter(published=True, geographic_entity=True)
    serializer_class = LocationSerializer
    filterset_fields = ("category", "community")
    filter_backends = (InBBoxFilter, filters.DjangoFilterBackend)
    throttle_scope = "read-only"
    bbox_filter_field = "point"

    def get_queryset(self):
        """
        Optionally restricts the returned POIs by filtering against a `search`
        query parameter in the URL.
        """
        queryset = self.queryset
        if search_phrase := self.request.query_params.get("search"):
            return queryset.annotate(
                search=SearchVector(
                    "name",
                    "description",
                    "category__label_singular",
                    "category__label_plural",
                    config="romanian",
                )
            ).filter(search=str(search_phrase))
        return queryset


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsApprovedUserOrReadOnly]
    queryset = Category.objects.all().order_by("label_plural")
    serializer_class = CategorySerializer
    throttle_scope = "read-only"


class CommunityViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer

    def perform_create(self, serializer):
        serializer.save(admin_users=[self.request.user])


"""
Generic views
"""


class LocationProposalView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = LocationProposalSerializer
    throttle_scope = "location-proposal"
