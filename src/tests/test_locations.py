from http import HTTPStatus

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

    response = client.get("/api/locations/")
    assert response.status_code == HTTPStatus.OK

    response_body = response.json()
    assert len(response_body["features"]) == 1

    feature_properties = response_body["features"][0]["properties"]
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

    response = client.get("/api/locations/")
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()["features"]) == 0
