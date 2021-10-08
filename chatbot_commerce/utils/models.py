"""Django models utilities."""

from slugify import slugify
# Django
from django.db import models
from django.utils.translation import gettext as _


class ChatbootModel(models.Model):
    """Chatboot commerce base model.

    Chatboot commerce acts as an abstract base class from which every
    other model in the project will inherit. This class provides
    every table with the following attributes:
        + created (DateTime): Store the datetime the object was created.
        + modified (DateTime): Store the last datetime the object was modified.
    """

    created = models.DateTimeField(
        'created at',
        auto_now_add=True,
        help_text='Date time on which the object was created.'
    )
    modified = models.DateTimeField(
        'modified at',
        auto_now=True,
        help_text='Date time on which the object was last modified.'
    )

    class Meta:
        """Meta option."""

        abstract = True

        get_latest_by = 'created'
        ordering = ['-created', '-modified']


class BaseRawAbstract(ChatbootModel):

    # Raw_data
    raw_json = models.JSONField(_("Raw data"), null=True, blank=True)

    # Hack to db
    serializer_data = models.JSONField(null=True, blank=True)

    class Meta:
        """Meta option."""
        abstract = True


class BaseAbstract(BaseRawAbstract):

    # Filter data
    name = models.CharField(
        max_length=500,
        null=True, blank=True
    )
    external_id = models.BigIntegerField(
        _("External ID"),
        db_index=True
    )

    class Meta:
        """Meta option."""
        abstract = True


class AbstractCategory(BaseAbstract):

    # Filter data
    slug_name = models.SlugField(
        max_length=255,
        null=True, blank=True
    )
    title = models.TextField(
        null=True, blank=True
    )

    # Extra data
    description = models.TextField(
        null=True, blank=True
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug_name = slugify(self.name, separator="_")
        return super().save(*args, **kwargs)

    class Meta:
        """Meta option."""
        abstract = True
