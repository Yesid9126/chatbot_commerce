"""Stores model."""

# Raw
from slugify import slugify

# Django
from django.db import models
from django.db.models.fields import SlugField

# utilities
from chatbot_commerce.utils.models import ChatbootModel


class Store(ChatbootModel):
    """Stores model."""

    name = models.CharField(
        max_length=255
    )
    slug_name = models.SlugField(max_length=50, unique=True, null=True, blank=True)

    url_enviroment = models.CharField(
        max_length=500
    )

    api_key = models.CharField(
        max_length=500
    )

    api_token = models.CharField(
        max_length=500
    )

    def __str__(self):
        """Return store name."""
        return f'Store:{self.name}'

    class Meta:
        verbose_name = "Store"
        verbose_name_plural = "Stores"

    @property
    def headers(self):
        headers = {
            "X-VTEX-API-AppKey": f"{self.api_key}",
            "X-VTEX-API-AppToken": f"{self.api_token}"
        }
        return headers

    def save(self, *args, **kwargs):
        self.slug_name = slugify(self.name, separator="_")
        return super().save(*args, **kwargs)
