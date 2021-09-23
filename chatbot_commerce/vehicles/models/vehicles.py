from django.db import models
from django.utils.translation import gettext as _


# Create your models here.
class Brand(models.Model):
    name = models.CharField(max_length=500, null=True, blank=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Brand"
        verbose_name_plural = "Brands"


class Model(models.Model):
    brand = models.ForeignKey(
        "vehicles.Brand",
        verbose_name=_("Brand"),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    name = models.CharField(
        _("Name"),
        max_length=500,
        null=True,
        blank=True,
    )
    description = models.CharField(
        _("Description"), max_length=50, null=True, blank=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Model"
        verbose_name_plural = "Models"


class ModelYear(models.Model):
    year = models.IntegerField(_("Year"), null=True, blank=True)
    model = models.ForeignKey(
        "vehicles.Model",
        verbose_name=_(""),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.year

    class Meta:
        verbose_name = "ModelYear"
        verbose_name_plural = "ModelYears"


class Vehicle(models.Model):
    brand = models.ForeignKey(
        "vehicles.Brand",
        verbose_name=_("Brand"),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    model = models.ForeignKey(
        "vehicles.Model",
        verbose_name=_("Model"),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    model_year = models.ForeignKey(
        "vehicles.ModelYear",
        verbose_name=_("Model year"),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.brand} {self.model} {self.model_year}"

    class Meta:
        verbose_name = "Vehicle"
        verbose_name_plural = "Vehicles"


class SkuVehicle(models.Model):
    vehicle = models.ForeignKey(
        "vehicles.vehicle",
        verbose_name=_("SkuVehicle"),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    description = models.TextField(_("Description"), blank=True, null=True)
    es_flota = models.BooleanField(("Es flota"), null=True, blank=True)
    created_date = models.DateTimeField(
        "created at",
        auto_now_add=True,
    )
    modified = models.DateTimeField(
        "modified at",
        auto_now=True,
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
    # model_year = models.IntegerField(
    #     _("Model year"),
    #     null=True,
    #     blank=True,
    # )
    # model_id = models.CharField(
    #     _("Model id"),
    #     max_length=500,
    #     null=True,
    #     blank=True
    # )
    manifest = models.CharField(
        _("Manifest"),
        max_length=500,
        null=True,
        blank=True,
    )
    article_nit = models.CharField(
        _("Nit article"),
        max_length=500,
        null=True,
        blank=True,
    )
    license_plate = models.CharField(
        _("Nit"),
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
    warranty_expiration = models.DateField(
        _("Warrranty expiration"),
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
        _("Insurance nit"),
        max_length=500,
        null=True,
        blank=True,
    )
    color = models.CharField(
        _("Color"),
        max_length=500,
        null=True,
        blank=True,
    )
    color_description = models.TextField(
        _("Color description"),
        null=True,
        blank=True,
    )
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
        _("Engine displacement"),
        max_length=500,
        null=True,
        blank=True,
    )
    capacity_unit_desc = models.CharField(
        _("Capatity unit description"),
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
    engine = models.CharField(
        _("Engine"),
        max_length=500,
        null=True,
        blank=True,
    )
    kilometraje = models.FloatField(
        "kilometraje",
        blank=True,
        null=True,
    )
    doors = models.FloatField(_("Car doors"), null=True, blank=True)
    fuel = models.CharField(_("Fuel"), max_length=500, null=True, blank=True)
    fuel_description = models.CharField(
        _("Fuel description"), max_length=500, null=True, blank=True
    )

    class Meta:
        verbose_name = "SkuVehicle"
        verbose_name_plural = "SkuVehicles"


class Price(models.Model):
    base_price = models.PositiveIntegerField(_("Price"), null=True, blank=True)
    sku_vehicle = models.ForeignKey(
        "vehicles.vehicle",
        verbose_name=_(""),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Price"
        verbose_name_plural = "Prices"


class Sales(models.Model):
    customer_nit = models.CharField(
        _("Buyer nit"),
        max_length=500,
        null=True,
        blank=True,
    )
    sales_type = models.CharField(  # Choosefield?
        _("Sales type"), max_length=500, null=True, blank=True
    )
    sales_type_desc = models.CharField(  # TODO preguntar que es
        _("Des sales type "),
        max_length=500,
        blank=True,
        null=True,
    )
    sales_plan = models.FloatField(
        _("Sales Plan"),
        blank=True,
        null=True,
    )
    sales_plan_desc = models.CharField(
        _("Des Tipo Venta"), max_length=500, null=True, blank=True
    )
    date_sale = models.DateField(_("Date Field"), auto_now=False, auto_now_add=False)
    fecha_obligatorio = models.DateField(  # TODO pregutar qué es.
        _("Fecha obligatorio"),
        auto_now=False,
        auto_now_add=False,
        null=True,
        blank=True,
    )
    user_nit = models.CharField(  # TODO preguntar qué es.
        _("User nit"), max_length=500, null=True, blank=True
    )
    year = models.IntegerField(_("year"), null=True, blank=True)

    class Meta:
        verbose_name = "Sale"
        verbose_name_plural = "Sales"
