from django.contrib import admin

from chatbot_commerce.vehicles.models.vehicles import Vehicle  # Sales


# Register your models here.
@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    """Vehicle model admin."""

    list_display = ["brand", "model", "model_year"]
    search_fields = ["brand", "model", "model_year"]
