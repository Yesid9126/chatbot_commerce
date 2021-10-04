from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six

from chatbot_commerce.stores.models import StoreAPIKey


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, store_api: "StoreAPIKey", timestamp: int) -> str:
        return (
            six.text_type(store_api.email) + six.text_type(timestamp) +
            six.text_type(store_api.prefix)
        )


api_key_activation_token = TokenGenerator()
