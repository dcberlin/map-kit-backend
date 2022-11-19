from django_filters import rest_framework as filters
from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser,
    AllowAny,
)
from django.contrib.postgres.search import SearchVector
from rest_framework import generics, viewsets
from rest_framework_gis.filters import InBBoxFilter
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Community, Location
from .serializers import (
    CategorySerializer,
    CommunitySerializer,
    LocationProposalSerializer,
    LocationSerializer,
    PlainLocationSerializer,
    UserSerializer,
)
from .permissions import IsApprovedUser, IsCommunityAdmin, ReadOnly


"""
ViewSets
"""


class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [ReadOnly]
    queryset = Location.objects.select_related("category").filter(
        published=True,
        geographic_entity=True,
    )
    serializer_class = LocationSerializer
    filterset_fields = ("category", "community", "community__path_slug")
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


class LocationAdminViewSet(viewsets.ModelViewSet):
    permission_classes = [
        (IsApprovedUser & IsCommunityAdmin) | (IsAuthenticated & ReadOnly)
    ]
    queryset = Location.objects.filter()
    serializer_class = PlainLocationSerializer
    filterset_fields = ("category", "community")
    filter_backends = (filters.DjangoFilterBackend,)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return self.queryset.filter(community__admin_users__in=[self.request.user])
        return self.queryset


class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser | ReadOnly]
    queryset = Category.objects.all().order_by("label_plural")
    serializer_class = CategorySerializer
    throttle_scope = "read-only"


class CommunityViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [ReadOnly]
    filterset_fields = ("path_slug",)
    filter_backends = (filters.DjangoFilterBackend,)
    queryset = Community.objects.filter(approved=True, published=True)
    serializer_class = CommunitySerializer


class CommunityAdminViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CommunitySerializer

    def perform_create(self, serializer):
        serializer.save(admin_users=[self.request.user])

    def get_queryset(self):
        return Community.objects.filter(admin_users__in=[self.request.user])


"""
Generic views
"""


class LocationProposalView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = LocationProposalSerializer
    throttle_scope = "location-proposal"


class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
