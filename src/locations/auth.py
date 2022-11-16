import hashlib
from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from django.core.cache import cache


class MapKitOIDCAuthenticationBackend(OIDCAuthenticationBackend):
    def create_user(self, claims):
        user = super(MapKitOIDCAuthenticationBackend, self).create_user(claims)

        user.username = claims.get("email", "")
        user.save()

        return user

    def update_user(self, user, claims):
        user.username = claims.get("email", "")
        user.save()

        return user

    def get_userinfo(self, *args, **kwargs):
        token = args[0].encode()
        token_hash = hashlib.sha256(token).hexdigest()
        cache_hit = cache.get(token_hash)
        if cache_hit is None:
            response = super().get_userinfo(*args, **kwargs)
            cache.set(token_hash, response, 60)
            return response
        return cache_hit
