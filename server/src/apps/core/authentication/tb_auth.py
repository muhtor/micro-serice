from rest_framework.authentication import get_authorization_header
from django.utils.translation import gettext_lazy as _
from apps.accounts.models import TBUserToken
from .auth_exceptions import AuthenticationFailed


class TBTokenAuthentication:

    keyword = 'Token'
    model = None

    def get_model(self):
        if self.model is not None:
            return self.model
        return TBUserToken

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = _('Invalid token header. No credentials provided.')
            raise AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid token header. Token string should not contain spaces.')
            raise AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = _('Invalid token header. Token string should not contain invalid characters.')
            raise AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise AuthenticationFailed(_('Invalid token.'))

        if not token.user.is_active:
            raise AuthenticationFailed(_('User inactive or deleted.'))

        return (token.user, token)

    def authenticate_header(self, request):
        print("REQUEST....", request)
        return self.keyword
