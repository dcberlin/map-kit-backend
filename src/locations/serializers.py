from django.contrib.gis.geos import Point, Polygon
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from .helpers import get_coordinates_from_address
from .models import Location, Category, Community, User


class CommunitySerializer(serializers.ModelSerializer):
    bbox = serializers.ListField(child=serializers.FloatField(), required=False)
    approved = serializers.BooleanField(read_only=True)

    def validate_bbox(self, value):
        Polygon.from_bbox(tuple(value))
        return value

    def validate(self, data):
        published = data.get("published")
        community = self.instance or Community(**data)
        if published and not community.has_minimum_pois():
            raise serializers.ValidationError(
                "A community map must have at least 2 published POIs to be published."
            )
        return data

    class Meta:
        model = Community
        fields = [
            "pk",
            "name",
            "description",
            "approved",
            "published",
            "bbox",
            "path_slug",
        ]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "pk",
            "name_slug",
            "color",
            "label_singular",
            "label_plural",
        ]


class LocationSerializer(GeoFeatureModelSerializer):
    """
    GeoJSON locations
    """

    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field="name_slug",
    )
    category_label = serializers.CharField(
        source="category.label_singular", read_only=True, default=""
    )
    pin_color = serializers.CharField(
        source="category.color", read_only=True, default="#fff"
    )
    community = serializers.PrimaryKeyRelatedField(
        queryset=Community.objects.all(),
        required=True,
    )

    class Meta:
        model = Location
        geo_field = "point"
        fields = [
            "pk",
            "community",
            "name",
            "address",
            "website",
            "email",
            "description",
            "category",
            "phone",
            "geographic_entity",
            "inexact_location",
            "published",
            "pin_color",
            "category_label",
        ]


class PlainLocationSerializer(serializers.ModelSerializer):
    """
    Non-GeoJSON locations (for admin endpoints etc.)
    """

    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field="name_slug",
    )
    category_label = serializers.CharField(
        source="category.label_singular", read_only=True, default=""
    )
    pin_color = serializers.CharField(
        source="category.color", read_only=True, default="#fff"
    )
    community = serializers.PrimaryKeyRelatedField(
        queryset=Community.objects.all(),
        required=True,
    )

    def to_internal_value(self, data):
        if address := data.get("address"):
            if coordinates := get_coordinates_from_address(address):
                data["point"] = Point(*coordinates)
            else:
                raise serializers.ValidationError(
                    {"address": ["Could not find coordinates for this address."]}
                )
        return super().to_internal_value(data)

    class Meta:
        model = Location
        geo_field = "point"
        fields = [
            "pk",
            "community",
            "name",
            "address",
            "website",
            "email",
            "description",
            "category",
            "phone",
            "geographic_entity",
            "inexact_location",
            "published",
            "pin_color",
            "category_label",
            "point",
        ]


class LocationProposalSerializer(GeoFeatureModelSerializer):
    """
    This serializer is used only when new location proposals are submitted.
    It covers a restricted set of fields. The rest of the fields have to be
    filled in by content reviewers.
    """

    user_submitted = serializers.HiddenField(default=True)

    def to_internal_value(self, data):
        if address := data.get("address"):
            if coordinates := get_coordinates_from_address(address):
                data["point"] = Point(*coordinates)
            else:
                raise serializers.ValidationError(
                    {"address": ["Could not find coordinates for this address."]}
                )
        return super().to_internal_value(data)

    class Meta:
        model = Location
        geo_field = "point"
        fields = [
            "name",
            "address",
            "website",
            "email",
            "description",
            "phone",
            "user_submitted",
            "community",
            "point",
        ]
        extra_kwargs = {
            field: {"required": True}
            for field in ["name", "address", "description", "community"]
        }


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "approved",
        ]
