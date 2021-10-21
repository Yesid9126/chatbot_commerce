from rest_framework.authentication import BaseAuthentication, CSRFCheck
from rest_framework import exceptions
from django.utils.translation import gettext_lazy as _
from chatbot_commerce.stores.models import StoreAPIKey


class StoreAPIKeyAuthentication(BaseAuthentication):

    keyword = 'Athorization'
    model = StoreAPIKey

    def get_model(self):
        if self.model is not None:
            return self.model
        from rest_framework_api_key.models import APIKey
        return APIKey

    def enforce_csrf(self, request):
        """
        Enforce CSRF validation for session based authentication.
        """
        def dummy_get_response(request):  # pragma: no cover
            return None

        check = CSRFCheck(dummy_get_response)
        # populates request.META['CSRF_COOKIE'], which is used in process_view()
        check.process_request(request)
        reason = check.process_view(request, None, (), {})
        if reason:
            # CSRF failed, bail with explicit error message
            raise exceptions.PermissionDenied('CSRF Failed: %s' % reason)

    def authenticate(self, request):
        auth = request.headers.get('Authorization').split('Api-Key ')

        if len(auth) < 1:
            msg = _('Invalid api key header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 1:
            msg = _('Invalid api key header. Credentials string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        auth = StoreAPIKey.objects.is_valid(auth)  # False or True

        self.enforce_csrf(request)

        return super().authenticate(request)

    def authenticate_credentials(self, key):
        model = self.get_model()

        try:
            key = model.objects.select_related('store').is_valid(key=key)  # True or False
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid api key.'))

        return (key, None)

    def authenticate_header(self, request):
        return self.keyword
