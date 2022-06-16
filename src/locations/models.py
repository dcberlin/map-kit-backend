from django.contrib.gis.db import models as gis_models
from django.contrib.postgres.fields import ArrayField
from django.db import models


class Community(gis_models.Model):
    name = models.CharField(null=True, blank=True, max_length=128)
    description = models.TextField(null=True, blank=True, max_length=500)
    bbox = ArrayField(models.FloatField(), size=4, null=True)
    published = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Communities"


class Location(gis_models.Model):
    name = models.CharField(
        max_length=64,
    )
    address = models.CharField(null=True, blank=True, max_length=128)
    website = models.CharField(null=True, blank=True, max_length=128)
    email = models.CharField(null=True, blank=True, max_length=128)
    phone = models.CharField(null=True, blank=True, max_length=32)
    description = models.TextField(null=True, blank=True, max_length=500)
    point = gis_models.PointField(
        null=True,
        blank=True,
    )
    geographic_entity = models.BooleanField(default=True)
    published = models.BooleanField(default=False)
    inexact_location = models.BooleanField(default=False)
    user_submitted = models.BooleanField(default=False)
    category = models.ForeignKey("Category", null=True, on_delete=models.CASCADE)
    community = models.ForeignKey("Community", null=True, on_delete=models.SET_NULL)

    @property
    def coordinates(self):
        if self.point:
            return self.point.coords

    def __str__(self):
        return self.name


class Category(models.Model):
    name_slug = models.SlugField(null=False, blank=False)
    label_singular = models.CharField(max_length=64, null=False, blank=False)
    label_plural = models.CharField(max_length=64, null=False, blank=False)

    def __str__(self):
        return self.name_slug

    class Meta:
        verbose_name_plural = "Categories"
