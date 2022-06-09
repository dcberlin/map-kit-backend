import pytest
from locations.models import Category, Location


@pytest.mark.django_db
def test_get_published_location(client):
    category_name = "Consiliere"
    location_name = "Biroul X"
    category = Category(label_singular=category_name)
    category.save()
    location = Location(
        name=location_name,
        published=True,
        category=category,
    )
    location.save()

    response = client.get("/api/locations/").json()
    assert len(response["features"]) == 1
    feature_properties = response["features"][0]["properties"]
    assert feature_properties["name"] == location_name
    assert feature_properties["category"]["label_singular"] == category_name


@pytest.mark.django_db
def test_get_unpublished_location(client):
    category_name = "Consiliere"
    location_name = "Biroul X"
    category = Category(label_singular=category_name)
    category.save()
    location = Location(
        name=location_name,
        published=False,
        category=category,
    )
    location.save()

    response = client.get("/api/locations/").json()
    assert len(response["features"]) == 0
