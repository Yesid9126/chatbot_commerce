"""Django models utilities."""
from slugify import slugify

# Django
from django.db import models
from django.contrib.postgres.fields import ArrayField
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
        _('created at'),
        auto_now_add=True,
        help_text='Date time on which the object was created.'
    )
    modified = models.DateTimeField(
        _('modified at'),
        auto_now=True,
        help_text='Date time on which the object was last modified.'
    )
    first_time = models.BooleanField(
        _("First time"),
        default=True,
        help_text='Was saved in database before.',
        editable=False
    )

    class Meta:
        """Meta option."""

        abstract = True

        get_latest_by = 'created'


class BaseRawAbstract(ChatbootModel):

    # Raw_data
    raw_json = models.JSONField(_("Raw data"), null=True, blank=True)

    class Meta:
        """Meta option."""
        abstract = True


class BaseExternalIdAbstract(models.Model):

    external_id = ArrayField(models.CharField(max_length=250), default=list)

    class Meta:
        """Meta option"""
        abstract = True


class BaseSlugnameAbstract(ChatbootModel):

    # Filter data
    name = models.CharField(
        _("Name"),
        max_length=500,
        null=True, blank=True, unique=True
    )
    slug_name = models.SlugField(
        max_length=255,
        null=True, blank=True, unique=True
    )

    def save(self, *args, **kwargs):
        self.slug_name = slugify(self.name, separator="_")
        return super().save(*args, **kwargs)

    class Meta:
        """Meta option."""
        abstract = True


class BaseAbstract(BaseRawAbstract):

    # Filter data
    name = models.CharField(
        _("Name"),
        max_length=500,
        null=True, blank=True
    )
    external_id = models.BigIntegerField(
        _("External ID"),
        null=True, blank=True
    )

    class Meta:
        """Meta option."""
        abstract = True


class AbstractCategory(BaseAbstract):

    # Filter data
    title = models.TextField(
        null=True, blank=True
    )

    # Extra data
    description = models.TextField(
        null=True, blank=True
    )

    def __str__(self):
        return self.name

    class Meta:
        """Meta option."""
        abstract = True


def super_save(instance):
    if instance.first_time:
        instance.first_time = False
        instance.super().save()
