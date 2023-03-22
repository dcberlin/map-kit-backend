import html
import json

from anymail.message import AnymailMessage
from django.conf import settings
from django.contrib.postgres.search import SearchVector
from django_filters import rest_framework as filters
from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser,
    AllowAny,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_gis.filters import InBBoxFilter

from locations.signals import location_data, try_send_email
from .models import Category, Community, Location
from .permissions import IsApprovedUser, IsCommunityAdmin, ReadOnly
from .serializers import (
    CategorySerializer,
    CommunitySerializer,
    LocationProposalSerializer,
    LocationSerializer,
    PlainLocationSerializer,
    UserSerializer,
)

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

    @action(methods=["post"], detail=True, permission_classes=[AllowAny])
    def flag(self, request, pk=None):
        """
        Flag a location
        """
        location = self.get_object()

        (
            admin_location_url,
            community_public_url,
            manager_location_url,
            tpl_data,
        ) = location_data(location)

        tpl_data["reason"] = html.escape(request.data.get("text"))
        tpl_data["email"] = html.escape(request.data.get("email"))
        tpl_data["phone"] = html.escape(request.data.get("phone"))

        # mail the community managers
        email = AnymailMessage(
            template_id="d-0027bd8f47014d0f8db249acd97939ce",
            subject="A fost raportată o locație",
            body=f"Tocmai a fost raportată locația {location.name} din comunitatea ta <a href='{community_public_url}'>{location.community.name}</a>. \n"
            f"Te rog să verifici și să o publici dacă este corectă. \n"
            f"Poți face acest lucru <a href='{manager_location_url}'>aici</a>",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=location.community.admin_users_emails(),
            bcc=[settings.SUPERADMIN_CONTACT_EMAIL],
        )
        email.template_id = "d-0027bd8f47014d0f8db249acd97939ce"
        email.dynamic_template_data = tpl_data
        email.merge_global_data = tpl_data
        try_send_email(email)

        # mail admin
        phone = (
            f" (tel: {html.escape(request.data.get('phone'))})"
            if request.data.get("phone")
            else ""
        )
        email = AnymailMessage(
            template_id="d-a7a22635a4744c829b951760d76ac8f4",
            subject="flag locatie",
            body=f"Locația '{location.name}' din comunitatea {location.community.name} "
            f"a fost raportată de {html.escape(request.data.get('email'))}{phone} pentru următorul motiv: \n\n"
            f"<b>{html.escape(request.data.get('text'))}</b>\n\n"
            f"Managerii comunității ({location.community.admin_users_emails()}) au fost anunțați.",
            to=[settings.SUPERADMIN_CONTACT_EMAIL],
        )
        email.dynamic_template_data = tpl_data
        email.merge_global_data = tpl_data
        try_send_email(email)

        return Response(status=200)

    @action(
        methods=["post"],
        url_path="propose-change",
        detail=True,
        permission_classes=[AllowAny],
    )
    def propose_change(self, request, pk=None):
        """
        Propose changed for a location
        """
        location = self.get_object()

        (
            admin_location_url,
            community_public_url,
            manager_location_url,
            tpl_data,
        ) = location_data(location)

        tpl_data["changes"] = json.dumps(request.data, indent=4)

        email = AnymailMessage(
            subject="Cerere modificare locație",
            body=f"Tocmai a propus cineva schimbări la locația {location.name} "
            f"din comunitatea ta <a href='{community_public_url}'>{location.community.name}. \n"
            f"Te rog verifică și <a href='{manager_location_url}'>schimbă locația</a> manual dacă e cazul. \n\n"
            f"Propunerile sunt: \n\n"
            f"<pre>{tpl_data['changes']}</pre>",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=location.community.admin_users_emails(),
            bcc=[settings.SUPERADMIN_CONTACT_EMAIL],
        )
        email.template_id = "d-4ebe3b84eebf408fb4d72d019d5b4801"
        email.merge_global_data = tpl_data
        try_send_email(email)

        return Response(status=200)


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
