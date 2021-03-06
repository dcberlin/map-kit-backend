import time

from django.contrib.auth.admin import UserAdmin
from django.contrib.gis import admin

from .models import Location, Category, Community, User
from .helpers import set_coordinates_from_address


@admin.action(description="Mark selected locations as published")
def make_published(modeladmin, request, queryset):
    queryset.update(published=True)


@admin.action(description="Geocode the addresses of the selected locations")
def make_geocoded(modeladmin, request, queryset):
    locations = queryset.filter(address__isnull=False)
    for location in locations:
        set_coordinates_from_address(location.address, location)
        time.sleep(0.5)


@admin.register(User)
class User(UserAdmin):
    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("approved",)}),)


@admin.register(Location)
class LocationAdmin(admin.GISModelAdmin):
    list_display = (
        "name",
        "category",
        "address",
        "published",
        "coordinates",
        "user_submitted",
    )
    actions = [make_published, make_geocoded]

    default_lon = 1489458
    default_lat = 6894156
    default_zoom = 10

    def save_model(self, request, obj, form, change):
        """
        Try to geocode any provided address while saving the model.
        """
        if "address" in form.changed_data or not obj:
            new_address = form.data["address"]
            set_coordinates_from_address(new_address, obj)

        super().save_model(request, obj, form, change)


@admin.register(Category)
class CategoryAdmin(admin.GISModelAdmin):
    verbose_name = "Categories"


@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    verbose_name = "Communities"
