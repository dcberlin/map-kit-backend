from django.apps import AppConfig
from django.core.signals import request_finished


class LocationsConfig(AppConfig):
    name = "locations"

    def ready(self):
        # Implicitly connect signal handlers decorated with @receiver.
        from . import signals

        # Explicitly connect a signal handler.
        request_finished.connect(signals.notify_on_community_proposal)
