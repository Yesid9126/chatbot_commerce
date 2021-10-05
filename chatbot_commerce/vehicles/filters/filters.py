import django_filters
from django import forms

from chatbot_commerce.vehicles.models.vehicles import Vehicle


class VehicleFilter(django_filters.FilterSet):

    brand = django_filters.CharFilter(
        lookup_expr="icontains",
        widget=forms.TextInput(attrs={"class": "form-control-mustard", "type": "text"}),
    )
    model = django_filters.CharFilter(
        lookup_expr="icontains",
        widget=forms.TextInput(attrs={"class": "form-control-mustard", "type": "text"}),
    )
    model_year = django_filters.CharFilter(
        lookup_expr="icontains",
        widget=forms.TextInput(attrs={"class": "form-control-mustard", "type": "text"}),
    )
    reference_id = django_filters.CharFilter(
        lookup_expr="icontains",
        widget=forms.TextInput(attrs={"class": "form-control-mustard", "type": "text"}),
    )

    class meta:
        models = Vehicle
        fields = ["brand", "model", "model_year", "brand_desc", "reference_id"]
        labels = {
            "brand": "Brand",
            "model": "Model",
            "model_year": "Year",
            "reference_id": "Reference",
        }
        # fields = '__all__'
