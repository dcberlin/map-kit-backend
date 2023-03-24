import html
import logging

from anymail.message import AnymailMessage
from django.conf import settings
from django.core import mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from locations.models import Community
from locations.models import Location


@receiver(post_save, sender=Community)
def on_community_proposal(**kwargs):
    if kwargs.get("created") is False:
        return  # We only want to send emails for new community proposals

    community: Community = kwargs.get("instance")
    url_community, url_community_manager, tpl_data = community_data(community)

    email = AnymailMessage(
        subject="A fost propusă o nouă comunitate",
        template_id=settings.SENDGRID_TPL_NEW_COMMUNITY_PROPOSAL,
        body=f"Tocmai a fost propusă comunitatea <a href='{settings.ADMIN_URL}locations/community/{community.id}/change/'>{community.name}</a>.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.SUPERADMIN_CONTACT_EMAIL],
    )
    email.merge_global_data = tpl_data
    try_send_email(email)


@receiver(post_save, sender=Location)
def on_location_proposal(**kwargs):
    if kwargs.get("created") is False:
        return  # We only want to send emails for new location proposals

    location: Location = kwargs.get("instance")

    if not location.community:
        return

    url_location_admin, url_community, url_community_manager, tpl_data = location_data(
        location
    )

    # then mail the community managers
    email = AnymailMessage(
        subject="A fost propusă o noua locație",
        template_id=settings.SENDGRID_TPL_NEW_LOCATION,
        body=f"Tocmai a fost propusă locația {location.name} în comunitatea ta {location.community.name}. Te rog să o verifici "
        f"și să o publici dacă este corectă. Poți face acest lucru <a href='{url_community_manager}'>aici</a>: "
        f"{url_community_manager}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=location.community.admin_users_emails(),
        bcc=[settings.SUPERADMIN_CONTACT_EMAIL],
    )
    email.merge_global_data = tpl_data

    try_send_email(email)


def community_data(community: Community):
    url_community = f"https://hartadiasporei.org/{community.path_slug}"
    url_community_manager = f"https://hartadiasporei.org/my-communities/{community.id}"
    tpl_data = {
        "community_id": community.id,
        "community_name": html.escape(community.name),
        "url_community": url_community,
        "url_community_manager": url_community_manager,
        "url_community_admin": f"https://hartadiasporei.org/admin/locations/community/{community.id}/change/",
        "community_managers": ", ".join(community.admin_users_emails()),
    }
    return url_community, url_community_manager, tpl_data


def location_data(location: Location):
    url_community = (
        f"https://hartadiasporei.org/{location.community.path_slug}"
        if location.community
        else ""
    )
    url_location_admin = (
        f"https://hartadiasporei.org/admin/locations/location/{location.id}/change/"
    )
    url_community_manager = (
        f"https://hartadiasporei.org/my-communities/{location.community.id}"
        if location.community
        else ""
    )
    tpl_data = {
        "location_id": location.id,
        "location_name": html.escape(location.name),
        "community_id": location.community.id if location.community else "",
        "community_name": html.escape(location.community.name)
        if location.community
        else "",
        "url_community": url_community,
        "url_community_manager": url_community_manager,
        "url_location_admin": url_location_admin,
        "community_managers": ", ".join(location.community.admin_users_emails())
        if location.community
        else "",
    }
    return url_location_admin, url_community, url_community_manager, tpl_data


def try_send_email(
    email: mail.EmailMessage | mail.EmailMultiAlternatives | AnymailMessage,
) -> bool:
    email.reply_to = [settings.SUPERADMIN_CONTACT_EMAIL]

    if email is AnymailMessage:
        email.tags = ["harta"]
        email.track_opens = True
        email.track_clicks = True
        email.attach_alternative(
            "<h1>da</h1>", "text/html"
        )  # single space; not an empty string

    try:
        email.send()
    except Exception as e:
        logging.warning(f"Failed to send email: {email.__dict__}")
        logging.warning(f"email backend: {settings.EMAIL_BACKEND}")
        logging.exception(e)
        return False
    return True
