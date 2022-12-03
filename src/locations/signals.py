from django.db.models.signals import post_save
from django.dispatch import receiver

from locations.models import Community


@receiver(post_save, sender=Community)
def notify_on_community_proposal(**kwargs):
    if kwargs.get("created") is True:
        instance = kwargs.get("instance")
        print(f"New community instance created: {instance!r}")
