from mozilla_django_oidc.auth import OIDCAuthenticationBackend


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
