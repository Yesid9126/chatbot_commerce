"""Stores model."""

# Raw
from slugify import slugify

# Django
from django.db import models
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives

# Models
from rest_framework_api_key.models import AbstractAPIKey, BaseAPIKeyManager
from rest_framework_api_key.crypto import KeyGenerator, concatenate, split

# Celery
from django_celery_beat.models import PeriodicTask, CrontabSchedule

# utilities
from chatbot_commerce.utils.models import ChatbootModel, BaseAbstract
from django.utils.translation import gettext as _
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
import requests
import typing


class MyKeyGenerator(KeyGenerator):
    def my_generate(self, key: str) -> typing.Tuple[str, str, str]:
        try:
            splited_key = key.split('.')
            prefix = splited_key[0]
            hashed_key = self.hash(key)
        except Exception as message:
            raise Exception(f'Incorrect key {message} you need a kwargs | key=(prefix).(secret_key) | for new hashed_key other wise use create_key instead create_my_key')
        return key, prefix, hashed_key


class StoreAPIKeyManager(BaseAPIKeyManager):
    key_generator = MyKeyGenerator()

    def get_usable_keys(self) -> models.QuerySet:
        return self.filter(revoked=False, is_active=True, email_status=True)

    def my_assign_key(self, obj: "StoreAPIKey", key: str, store_name: str) -> str:
        try:
            key, prefix, hashed_key = self.key_generator.my_generate(key=key)
        except Exception as message:
            raise Exception(f'todo mal {message}')
        else:
            pk = concatenate(prefix, hashed_key)

        obj.id = pk
        obj.prefix = prefix
        obj.hashed_key = hashed_key

        try:
            obj.store = Store.objects.get(name=store_name)
        except Exception:
            obj.store = None

        return key

    def create_my_key(self, **kwargs: typing.Any) -> typing.Tuple["StoreAPIKey", str]:
        kwargs.pop("id", None)
        key = kwargs.pop("key", None)
        name = kwargs.get("name")
        obj = self.model(**kwargs)
        key = self.my_assign_key(obj, key, name)
        obj.save()
        return obj, key

    def assign_key(self, obj: "StoreAPIKey") -> str:
        try:
            key, prefix, hashed_key = self.key_generator.generate()
        except ValueError:  # Compatibility with < 1.4
            generate = typing.cast(
                typing.Callable[[], typing.Tuple[str, str]], self.key_generator.generate
            )
            key, hashed_key = generate()
            pk = hashed_key
            prefix, hashed_key = split(hashed_key)
        else:
            pk = concatenate(prefix, hashed_key)

        obj.id = pk
        obj.prefix = prefix
        obj.hashed_key = hashed_key

        try:
            obj.store = Store.objects.get(name=self.name)
        except Exception:
            obj.store = None

        mail_subject = _('CHABOT API KEY')
        context = {
            'words': _('This is a new api key for your store just confirm your email and wait for chatbot active this key.'),
            'key': key,
        }
        template = get_template('api_key.html')
        content = template.render(context)
        to_email = obj.email

        email = EmailMultiAlternatives(
            mail_subject,
            'Your key',
            settings.EMAIL_HOST_USER,
            [to_email]
        )

        email.attach_alternative(content, 'text/html')
        email.send()

        return key

    def create_key(self, **kwargs: typing.Any) -> typing.Tuple["StoreAPIKey", str]:
        # Prevent from manually setting the primary key.
        kwargs.pop("id", None)
        name = kwargs.get("name")
        obj = self.model(**kwargs)
        key = self.assign_key(obj, name)
        obj.save()
        return obj, key

    def get_from_my_key(self, key: str, store_name: str) -> "StoreAPIKey":
        prefix, _, _ = key.partition(".")
        queryset = self.get_usable_keys()

        try:
            api_key = queryset.get(prefix=prefix, name=store_name)
        except self.model.DoesNotExist:
            raise  # For the sake of being explicit.

        if not api_key.is_valid(key):
            raise self.model.DoesNotExist("Key is not valid.")
        else:
            return api_key

    def is_my_valid(self, key: str, store_name: str) -> bool:
        try:
            api_key = self.get_from_my_key(key, store_name)
        except self.model.DoesNotExist:
            return False

        if api_key.has_expired:
            return False

        return True


class StoreAPIKey(AbstractAPIKey):
    """Store api keys model."""

    store = models.ForeignKey("Store", verbose_name=_("Store"), on_delete=models.CASCADE, null=True, blank=True, editable=False)
    is_active = models.BooleanField(_("Status"), default=False, editable=False)

    __original_email = None
    email = models.EmailField(_("E-mail"), max_length=254)
    email_status = models.BooleanField(_("Status email"), default=False, editable=False)

    objects = StoreAPIKeyManager()

    def __init__(self, *args: typing.Any, **kwargs: typing.Any):
        super().__init__(*args, **kwargs)
        self.__original_email = self.email

    def save(self, *args, **kwargs) -> None:
        store = self.store
        name = self.name
        if store:
            store_name = store.name
            if not name or name != store_name:
                self.name = store_name
        elif not store and name:
            try:
                self.store = Store.objects.get(name=name)
            except Exception as message:
                raise Exception(f"That store don't exists {message}")
        else:
            raise Exception("Need a store name or a store object first.")

        if self.email != self.__original_email:
            from chatbot_commerce.utils.token_email import api_key_activation_token
            mail_subject = _('CHATBOT CONFIRM EMAIL')
            context = {
                'words': _('confirm your email. this is required for new api key or when email address is changed'),
                'domain': settings.HOST,
                'uid': urlsafe_base64_encode(force_bytes(self.pk)),
                'token': api_key_activation_token.make_token(self),
            }
            template = get_template('confirm_email.html')
            content = template.render(context)
            to_email = self.email

            email = EmailMultiAlternatives(
                mail_subject,
                'Email confirmation',
                settings.EMAIL_HOST_USER,
                [to_email]
            )

            email.attach_alternative(content, 'text/html')
            email.send()

            self.email_status = False

        super().save(*args, **kwargs)
        self.__original_email = self.email

    class Meta(AbstractAPIKey.Meta):
        "Meta class"

        verbose_name = 'Store APIKey'
        verbose_name_plural = "Store APIKey's"
        default_related_name = "keys"


class Store(ChatbootModel):
    """Stores model."""

    STORE_TYPE = (
        ('VTEX', 'VTEX'),
    )

    # info filter
    store_type = models.CharField(_("Type of store"), max_length=500, choices=STORE_TYPE)
    name = models.CharField(_("Name of store"), max_length=255)
    slug_name = models.SlugField(max_length=50, null=True, blank=True)
    url_enviroment = models.CharField(_("Url enviroment"), max_length=500, blank=True, null=True)

    # Task manage
    sync_status = models.BooleanField(_("Task begun Finish"), default=False)
    creating_updating_elements_status = models.BooleanField(_("Task principal store elments"), default=False)

    # Request information
    domain = models.CharField(_("Domain of store"), max_length=500, blank=True, null=True)
    status = models.BooleanField(_("Valid connection"), default=False)
    api_key = models.CharField(max_length=500)
    api_token = models.CharField(max_length=500)

    # Filter manage
    disable_filters = models.BooleanField(_("Disable filters"), default=False)
    apply_filter_enable_products = models.BooleanField(_("Enable products"), default=True)
    apply_filter_enable_skus = models.BooleanField(_("Enable skus"), default=True)
    apply_filter_price = models.BooleanField(_("Valid price"), default=True)
    apply_filter_image = models.BooleanField(_("Valid image"), default=True)

    def __str__(self):
        """Return store name."""
        return f'{self.name}'

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

    @property
    def urls(self):
        if self.store_type == 'VTEX':
            urls = {
                "base_url": f'https://{self.name}.{self.url_enviroment}/api',
                "base_price_url": f'https://api.vtex.com/{self.name}',
                "status_url": f'https://{self.name}.{self.url_enviroment}/api/catalog_system/pvt/brand/list'
            }
        return urls

    def save(self, *args, **kwargs):
        if self.disable_filters:
            self.apply_filter_enable_products = False
            self.apply_filter_enable_skus = False
            self.apply_filter_image = False
            self.apply_filter_price = False
        try:
            r = requests.get(url=self.urls["status_url"], headers=self.headers, timeout=1000)
            if r.status_code in [requests.codes.ok]:
                self.status = True
            else:
                self.status = False
        except Exception:
            self.status = False
        self.slug_name = slugify(self.name, separator="_")
        return super().save(*args, **kwargs)


@receiver(post_save, sender=Store)
def execute_task(sender, instance, *args, **kwargs):
    if instance.status is True and instance.sync_status is False:
        from chatbot_commerce.products.tasks import store_begining
        store_begining.s(store=instance.pk).apply_async(countdown=5)

    if instance.sync_status is True:
        try:
            every_1, _ = CrontabSchedule.objects.get_or_create(day_of_week='*', hour=1, minute=0)
            task_instance, _ = PeriodicTask.objects.get_or_create(name=f'{instance.name} create & update', task='principal_periodic_task', defaults=dict(crontab=every_1, kwargs='{"store": "%s"}' % (instance.pk)))
        except Exception as message:
            print(message)

    if instance.status is False or instance.sync_status is False:
        PeriodicTask.objects.filter(name=f'{instance.name} create & update', task='principal_periodic_task').delete()


class SaleChannel(BaseAbstract):
    """Trade policy model."""

    # Filter data
    slug_name = models.SlugField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(_("Status"), default=False)

    # Relationship filter
    store = models.ForeignKey("Store", verbose_name=_("Store"), on_delete=models.CASCADE)
    sellers = models.ManyToManyField("Seller", verbose_name=_("Sellers"))

    def __str__(self):
        """Return store name."""
        return f'{self.store.name.capitalize()}: sale channel = {self.name}, ID = {self.external_id}'

    def save(self, *args, **kwargs):
        self.slug_name = slugify(self.name, separator="_")
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Sale Channel"
        verbose_name_plural = "Sales Channel"
        default_related_name = 'sales_channel'


class Seller(ChatbootModel):
    """Seller model."""

    # Filter data
    seller_id = models.CharField(_("Id of seller"), help_text=_("coud be a text instade a number"), max_length=500)
    name = models.CharField(_("Name of seller"), max_length=500, null=True, blank=True)
    slug_name = models.SlugField(max_length=50, null=True, blank=True)
    hibrit_payment_options = models.BooleanField(_("Various forms of payment"), default=False, null=True)
    is_active = models.BooleanField(_("Status"), default=False)

    # Relationship filter
    store = models.ForeignKey("Store", verbose_name=_("Store"), on_delete=models.CASCADE)

    # Extra data
    description = models.CharField(_("Description of seller"), max_length=500)

    # raw data
    raw_json = models.JSONField(_("Raw data"))

    def __str__(self):
        return f'{self.store} | {self.name}'

    def save(self, *args, **kwargs):
        self.slug_name = slugify(self.name, separator="_")
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Seller"
        verbose_name_plural = "Sellers"
        default_related_name = 'sellers'


class SkuSeller(ChatbootModel):

    # Filter data
    is_active = models.BooleanField(_("Status"))

    # Relationship filter
    sku = models.ForeignKey("products.Skus", verbose_name=_("Sku"), on_delete=models.CASCADE)
    seller = models.ForeignKey("Seller", verbose_name=_("Seller"), on_delete=models.CASCADE)

    # Raw data
    raw_json = models.JSONField(_("Raw data"))

    class Meta:
        verbose_name = 'Sku Seller'
        verbose_name_plural = 'Skus Sellers'
        default_related_name = 'sku_seller'
