from django.contrib.gis.geos import Point
from http import HTTPStatus
import pytest

from locations.models import Category, Community, Location, User


@pytest.fixture
def user_approved():
    user = User(approved=True)
    user.save()
    return user


@pytest.fixture
def user_unapproved():
    user = User()
    user.save()
    return user


@pytest.mark.django_db
def test_create_community(client, user_unapproved):
    community_name = "Berlin"
    client.force_login(user_unapproved)
    response = client.post(
        "/api/communities-admin/",
        {"name": community_name, "slug": "berlin"},
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json()["name"] == community_name


@pytest.mark.django_db
def test_create_community_with_location(client, user_approved):
    community_name = "Giessen"
    client.force_login(user_approved)
    category = Category(name_slug="bakery")
    category.save()

    # Create community
    com_response = client.post(
        "/api/communities-admin/",
        {"name": community_name, "slug": "giessen"},
    )
    assert com_response.status_code == HTTPStatus.CREATED
    community_pk = com_response.json()["pk"]

    # Create POI
    poi_response = client.post(
        "/api/locations-admin/",
        {
            "name": "Brutaria de la coltz",
            "community": community_pk,
            "category": category.name_slug,
        },
    )
    assert poi_response.status_code == HTTPStatus.CREATED
    location_pk = poi_response.json()["pk"]

    get_poi_response = client.get(
        f"/api/locations-admin/{location_pk}/",
    )

    # Publish location
    patch_poi_response = client.patch(
        f"/api/locations-admin/{location_pk}/",
        json={
            "published": True,
        },
    )
    assert patch_poi_response.status_code == HTTPStatus.OK

    # Publish community
    patch_com_response = client.patch(
        f"/api/communities-admin/{community_pk}/",
        json={
            "published": True,
        },
    )
    assert patch_com_response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_create_location_unapproved_user(client, user_unapproved):
    client.force_login(user_unapproved)
    response = client.post(
        "/api/locations-admin/",
        {"name": "Brutaria de la coltz"},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.django_db
def test_create_location_in_another_community(client, user_approved):
    client.force_login(user_approved)
    community = Community(name="Berlin")  # Community has no admins
    community.save()
    category = Category(name_slug="bakery")
    category.save()
    response = client.post(
        "/api/locations-admin/",
        {
            "name": "Brutaria de la coltz",
            "community": community.pk,
            "category": category.name_slug,
        },
    )
    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.django_db
def test_update_location_in_another_community(client, user_approved):
    client.force_login(user_approved)
    community_1 = Community(name="Berlin")  # Community has no admins
    community_1.save()
    community_2 = Community(name="Hamburg")  # Community has no admins
    community_2.save()
    category = Category(name_slug="bakery")
    category.save()
    location = Location(name="Brutaria de la coltz", community=community_1)
    response = client.put(
        f"/api/locations-admin/{location.pk}/",
        {
            "name": "Pwned",
            "category": category.name_slug,
            "community": community_2.pk,
        },
        content_type="application/json",
    )
    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.django_db
def test_create_location_authorized(client, user_approved):
    community = Community(name="Berlin")
    community.save()
    community.admin_users.set([user_approved])
    community.save()
    category = Category(name_slug="bakery", color="#fff")
    category.save()
    client.force_login(user_approved)
    response = client.post(
        "/api/locations-admin/",
        {
            "name": "Brutaria de la coltz",
            "category": category.name_slug,
            "community": community.pk,
        },
    )
    assert response.status_code == HTTPStatus.CREATED


@pytest.mark.django_db
def test_create_community_w_location_and_filter(client, user_approved):
    client.force_login(user_approved)

    category = Category(name_slug="bakery")
    category.save()
    community_name = "Harta Diasporei din Offenbach"
    offenbach_bbox = [8.692245, 50.076091, 8.837814, 50.139065]
    location_name = "Scoala de muzica"
    location_point = Point(8.792145, 50.092794)

    create_community_response = client.post(
        "/api/communities-admin/",
        {
            "name": community_name,
            "bbox": offenbach_bbox,
        },
    )
    assert create_community_response.status_code == HTTPStatus.CREATED
    assert create_community_response.json()["bbox"] == offenbach_bbox

    community_pk = create_community_response.json()["pk"]
    offenbach_location = Location(
        name=location_name,
        point=location_point,
        published=True,
        community=Community.objects.get(pk=community_pk),
        category=category,
    )
    offenbach_location.save()
    berlin_location = Location(
        name=location_name,
        point=Point(13.4267284, 52.5530381),
        published=True,
        category=category,
    )
    berlin_location.save()

    get_locations_response_bbox = client.get(
        f"/api/locations/?in_bbox={','.join(str(coord) for coord in offenbach_bbox)}",
    )
    assert get_locations_response_bbox.status_code == HTTPStatus.OK
    assert len(get_locations_response_bbox.json()["features"]) == 1

    get_locations_response_comm = client.get(
        f"/api/locations/?community={community_pk}",
    )
    assert get_locations_response_comm.status_code == HTTPStatus.OK
    assert len(get_locations_response_comm.json()["features"]) == 1
