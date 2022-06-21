from django.contrib.gis.geos import Polygon
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from .models import Location, Category, Community


class CommunitySerializer(serializers.ModelSerializer):
    bbox = serializers.ListField(child=serializers.FloatField(), required=False)

    def validate_bbox(self, value):
        Polygon.from_bbox(tuple(value))
        return value

    class Meta:
        model = Community
        fields = [
            "pk",
            "name",
            "description",
            "bbox",
        ]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "pk",
            "name_slug",
            "label_singular",
            "label_plural",
        ]


class LocationSerializer(GeoFeatureModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field="name_slug",
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
        ]


class LocationProposalSerializer(GeoFeatureModelSerializer):
    """
    This serializer is used only when new location proposals are submitted.
    It covers a restricted set of fields. The rest of the fields have to be
    filled in by content reviewers.
    """

    user_submitted = serializers.HiddenField(default=True)

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
        ]
        extra_kwargs = {
            field: {"required": True} for field in ["name", "address", "description"]
        }
