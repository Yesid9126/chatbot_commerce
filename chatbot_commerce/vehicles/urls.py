from django.urls import path

from .views.vehicles import (
    RegistrationView,
    VehicleDelete,
    VehiclesListView,
    VehicleUpdate,
)

app_name = "vehicles"

urlpatterns = [
    path("registration/", RegistrationView.as_view(), name="registration-vehicles"),
    path("list/", VehiclesListView.as_view(), name="list-vehicles"),
    path("remove/<slug>/", VehicleDelete.as_view(), name="remove-vehicle"),
    path("update/<slug>/", VehicleUpdate.as_view(), name="update-vehicle"),
]
