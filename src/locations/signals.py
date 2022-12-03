from django.core import mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from locations.models import Community


@receiver(post_save, sender=Community)
def notify_on_community_proposal(**kwargs):
    if kwargs.get("created") is True:
        instance = kwargs.get("instance")
        print(f"New community instance created: {instance!r}")
        email = mail.EmailMessage(
            subject=f"New community {instance.name} proposed!",
            body="A new community has been proposed.",  # TODO: Phrase a proper body
            from_email="from@example.com",  # TODO: Change to the real one
            to=["to1@example.com"],  # TODO: Change to the real one
        )
        email.send()
