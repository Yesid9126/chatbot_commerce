from django.db import models
from django.utils.translation import gettext as _


class Vehicle(models.Model):
    # TODO check the following fields:
    #   (kilometraje, fecha_obligatorio, usado_comprado, usado_retomado, es_flota)

    description = models.TextField(_("Description"), blank=True, null=True)
    engine_displacement = models.FloatField(
        _("Engine displacement"),
        null=True,
        blank=True,
    )
    capacity = models.FloatField(
        _("Capacity"),
        null=True,
        blank=True,
    )
    capacity_unit = models.CharField(
        _("Capacity unit"),
        max_length=500,
        null=True,
        blank=True,
    )
    capacity_unit_desc = models.CharField(
        _("Capacity unit description"),
        max_length=500,
        null=True,
        blank=True,
    )
    created_date = models.DateTimeField(
        ("Created at"),
        auto_now_add=True,
        null=True,
        blank=True,
    )
    reference_id = models.CharField(  # codigo
        _("Reference id"),
        max_length=500,
        null=True,
        blank=True,
    )
    series_id = models.CharField(
        _("Series id"),
        max_length=500,
        null=True,
        blank=True,
    )
    chassis = models.CharField(
        _("Chassis"),
        max_length=500,
        null=True,
        blank=True,
    )
    Engine = models.CharField(
        _("Engine"),
        max_length=500,
        null=True,
        blank=True,
    )
    model_year = models.IntegerField(
        _("Model year"),
        null=True,
        blank=True,
    )
    manifest = models.CharField(  # manifiesto
        _("Manifest"),
        max_length=500,
        null=True,
        blank=True,
    )
    article_nit = models.CharField(  # nit prenda
        _("Article nit"),
        max_length=500,
        null=True,
        blank=True,
    )
    kilometraje = models.FloatField(
        "kilometraje",
        blank=True,
        null=True,
    )
    license_plate = models.CharField(
        _("License plate"),
        max_length=500,
        null=True,
        blank=True,
    )
    city_license_plate = models.CharField(
        _("City car's license plate"),
        max_length=500,
        null=True,
        blank=True,
    )
    warranty_expiration = models.DateField(  # fecha fin garantia
        _("Warrranty expiration"),
        auto_now=False,
        auto_now_add=False,
        null=True,
        blank=True,
    )
    customer_nit = models.CharField(
        _("Customer nit"),
        max_length=500,
        null=True,
        blank=True,
    )
    sales_type = models.CharField(  # Choosefield?
        _("Sales type"), max_length=500, null=True, blank=True
    )
    sales_type_desc = models.CharField(
        _("Sales type description"),
        max_length=500,
        blank=True,
        null=True,
    )
    sales_plans = models.FloatField(
        _("Sales Plans"),
        blank=True,
        null=True,
    )
    sales_plan_desc = models.CharField(
        _("Sales plan description"), max_length=500, null=True, blank=True
    )
    date_sale = models.DateField(
        _("Date sale"), auto_now=False, auto_now_add=False, null=True, blank=True
    )
    fecha_obligatorio = models.DateField(  # pregutar qué es.
        ("Fecha obligatorio"),
        auto_now=False,
        auto_now_add=False,
        null=True,
        blank=True,
    )
    technical_mechanical_date = models.DateField(
        _("Tecnical-mechanical date"),
        auto_now=False,
        auto_now_add=False,
        null=True,
        blank=True,
    )
    insurance_nit = models.CharField(
        _("insurance nit"),
        max_length=500,
        null=True,
        blank=True,
    )
    user_nit = models.CharField(
        _("User nit"),
        max_length=500,
        null=True,
        blank=True,
    )
    doors = models.FloatField(
        _("Car doors"),
        null=True,
        blank=True,
    )
    year = models.IntegerField(  # TODO preguntar qué es.
        _("year"),
        null=True,
        blank=True,
    )
    model = models.CharField(
        _("Model"),
        max_length=500,
        null=True,
        blank=True,
    )
    model_id = models.CharField(
        _("Model id"),
        max_length=500,
        null=True,
        blank=True,
    )
    brand = models.CharField(
        _("Brand"),
        max_length=500,
        null=True,
        blank=True,
    )
    modelo_desc = models.CharField(
        _("Model description"),
        max_length=500,
        null=True,
        blank=True,
    )
    brand_desc = models.CharField(
        _("Brand description"),
        max_length=500,
        null=True,
        blank=True,
    )
    color = models.CharField(
        _("color"),
        max_length=500,
        null=True,
        blank=True,
    )
    color_desc = models.CharField(
        _("Color description"),
        max_length=500,
        null=True,
        blank=True,
    )
    unit_value = models.FloatField(
        _("Unit value"),
        null=True,
        blank=True,
    )
    fuel = models.CharField(
        _("Fuel"),
        max_length=500,
        null=True,
        blank=True,
    )
    fuel_description = models.CharField(
        _("Fuel description"),
        max_length=500,
        null=True,
        blank=True,
    )
    date_last_entry = models.DateField(
        _("Date last entry"),
        auto_now=False,
        auto_now_add=False,
        null=True,
        blank=True,
    )
    usado_comprado = models.FloatField(("Usado comprado"), null=True, blank=True)
    usado_retomado = models.FloatField(
        ("Usado retomado"),
        null=True,
        blank=True,
    )
    es_flota = models.BooleanField(
        ("Es flota"),
        null=True,
        blank=True,
    )
    transaction_id = models.CharField(
        _("Transaction id"),
        max_length=500,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Vehicle"
        verbose_name_plural = "Vehicles"
