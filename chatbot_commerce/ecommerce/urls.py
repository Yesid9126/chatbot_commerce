from django.urls import path

from chatbot_commerce.ecommerce.views import (
    HomeView,
    OrderListView,
    ProductDetailView,
    StoreListView,
    add_to_car,
    remove_from_cart,
    remove_one_from_cart,
)

app_name = "ecommerce"

urlpatterns = [
    path("<store>", HomeView.as_view(), name="home"),
    path("<store>/product/<external_id>/", ProductDetailView.as_view(), name="product"),
    path("<store>/order-list/", OrderListView.as_view(), name="order-list"),
    path("<store>/add-to-cart/<external_id>/", add_to_car, name="add-to-cart"),
    path(
        "<store>/remove-from-cart/<external_id>",
        remove_from_cart,
        name="remove-from-cart",
    ),
    path(
        "<store>/remove-one-from-cart/<external_id>",
        remove_one_from_cart,
        name="remove-one-from-cart",
    ),
    path("", StoreListView.as_view(), name="store"),
]
