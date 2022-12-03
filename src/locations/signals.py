from django.core import mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from locations.models import Community

COMMUNITY_PROPOSAL_TEMPLATE = (
    "Salut!\n\nCineva tocmai a propus comunitatea {community_name}. Intră "
    "pe Django admin (https://map-kit-api.diasporacivica.berlin/admin/) "
    "ca să aprobi comunitatea nouă şi userul, dacă încă nu este aprobat."
)


@receiver(post_save, sender=Community)
def notify_on_community_proposal(**kwargs):
    if kwargs.get("created") is True:
        instance = kwargs.get("instance")
        email_body = COMMUNITY_PROPOSAL_TEMPLATE.format(
            community_name=instance.name,
        )
        email = mail.EmailMessage(
            subject=f"O nouă comunitate a fost propusă!",
            body=email_body,
            from_email="harta@diasporacivica.berlin",
            to=["contact@diasporacivica.berlin"],
        )
        email.send()
