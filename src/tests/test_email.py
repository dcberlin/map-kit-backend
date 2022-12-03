from http import HTTPStatus

import pytest
from django.core import mail

from locations.models import User


def test_email_sanity(mailoutbox):
    """
    Do a sanity check to ensure that the testing setup for emails works.
    """
    email = mail.EmailMessage(
        subject="Sanity check",
        body="Hi there, nobody!",
        from_email="from@example.com",
        to=["to1@example.com"],
    )
    email.send()

    assert len(mailoutbox) == 1


@pytest.fixture
def user_unapproved():
    user = User()
    user.save()
    return user


@pytest.mark.django_db
def test_community_creation(user_unapproved, mailoutbox, client):
    client.force_login(user_unapproved)
    response = client.post(
        "/api/communities-admin/",
        {"name": "Berlin", "slug": "berlin"},
    )
    assert response.status_code == HTTPStatus.CREATED
    assert len(mailoutbox) == 1
