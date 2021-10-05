from django import forms

from chatbot_commerce.vehicles.models.vehicles import Vehicle


class VehiclesForm(forms.ModelForm):
    es_flota = forms.BooleanField(
        required=False,
        widget=(
            forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                    "id": "defaultCheck2",
                    "type": "checkbox",
                }
            )
        ),
    )

    def __init__(self, *args, **kwargs):
        super(VehiclesForm, self).__init__(*args, **kwargs)

        # apply class to all fields
        for field in self.fields.values():
            # if 'date' in field:
            if (
                isinstance(field, forms.CharField)
                or isinstance(field, forms.IntegerField)
                or isinstance(field, forms.FloatField)
            ):
                field.widget.attrs["class"] = "form-control"
                # field.widget.attrs['id'] = 'formrow-firstname-input'
                field.widget.attrs["type"] = "text"

        for name, field in self.fields.items():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs["rows"] = 1

    class Meta:
        model = Vehicle
        # field = '__all__'
        fields = (
            "brand",
            "model",
            "model_year",
            "description",
            "capacity",
            "capacity_unit",
            "capacity_unit_desc",
            # 'created_date',
            "reference_id",
            "series_id",
            "chassis",
            "engine",
            "engine_displacement",
            "manifest",
            "article_nit",
            "kilometraje",
            "license_plate",
            "city_license_plate",
            "warranty_expiration",
            "customer_nit",
            "sales_type",
            "sales_type_desc",
            "sales_plans",
            "sales_plan_desc",
            "date_sale",
            "fecha_obligatorio",
            "technical_mechanical_date",
            "insurance_nit",
            "user_nit",
            "doors",
            "year",
            "model_id",
            "model_desc",
            "brand_desc",
            "color",
            "color_desc",
            "unit_value",
            "fuel",
            "fuel_description",
            "date_last_entry",
            "usado_comprado",
            "usado_retomado",
            "es_flota",
            "transaction_id",
        )
        # exclude = ('created_date',)

        # custom widgets
        widgets = {
            "brand": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "aria-describedby": "emailHelp",
                    "placeholder": "Brand ",
                }
            ),
            "warranty_expiration": forms.DateInput(
                format=("%m/%d/%Y"),
                attrs={
                    "class": "form-control",
                    "placeholder": "Select a date",
                    "type": "date",
                },
            ),
            "technical_mechanical_date": forms.DateInput(
                format=("%m/%d/%Y"),
                attrs={
                    "class": "form-control",
                    "placeholder": "Select a date",
                    "type": "date",
                },
            ),
        }
