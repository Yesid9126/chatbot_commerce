import typing

from rest_framework_api_key.permissions import BaseHasAPIKey
from chatbot_commerce.stores.models import StoreAPIKey
from django.http import HttpRequest

class HasStoreAPIKey(BaseHasAPIKey):
    model = StoreAPIKey

    def get_store_name(self, request: HttpRequest) -> typing.Optional[str]:
        return self.key_parser.get_name(request)

    def has_permission(self, request: HttpRequest, view: typing.Any) -> bool:
        assert self.model is not None, (
            "%s must define `.model` with the API key model to use"
            % self.__class__.__name__
        )
        key = self.get_key(request)
        store_name = view.kwargs.get("store_slug_name")
        if not key or not store_name:
            return False
        return self.model.objects.is_my_valid(key, store_name)

class HasAPIKey(BaseHasAPIKey):
    model = StoreAPIKey
