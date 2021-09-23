from django.contrib import admin

from chatbot_commerce.vehicles.models.vehicles import (  # Sales
    Brand,
    Model,
    ModelYear,
    Price,
    SkuVehicle,
    Vehicle,
)

# Register your models here.


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """Brand model admin."""

    list_display = ["name", "description"]
    search_fields = ["name"]


@admin.register(Model)
class ModelAdmin(admin.ModelAdmin):

    list_display = ["name", "brand"]
    search_fields = ["name"]


@admin.register(ModelYear)
class ModelYearAdmin(admin.ModelAdmin):

    list_display = ["year", "model"]
    search_fields = ["year", "model"]


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    """Vehicle model admin."""

    list_display = ["brand", "model", "model_year"]
    search_fields = ["brand", "model", "model_year"]


@admin.register(SkuVehicle)
class SkuVehicleAdmin(admin.ModelAdmin):
    """SkuVehicle model admin."""

    list_display = ["vehicle"]


@admin.register(Price)
class priceAdmin(admin.ModelAdmin):

    list_display = ["base_price", "sku_vehicle"]
    search_fields = ["base_price"]
