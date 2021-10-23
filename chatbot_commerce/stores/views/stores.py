from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_text
from django.shortcuts import redirect
from django.conf import settings

from django.http import HttpResponse

from chatbot_commerce.stores.models import StoreAPIKey
from chatbot_commerce.utils.token_email import api_key_activation_token


def email_is_active(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        store_api = StoreAPIKey.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, StoreAPIKey.DoesNotExist):
        store_api = None
    if store_api and api_key_activation_token.check_token(store_api, token):
        store_api.verify = True
        store_api.is_active = True
        store_api.save()
        return redirect(f'http://{settings.HOST}/successfuly/email/')
    return HttpResponse('Activation link is invalid!')


def successfuly_email(request):
    return HttpResponse('Thank you for confirm your email, now wait for chatbot activate your api_key')
