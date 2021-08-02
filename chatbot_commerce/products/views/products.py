"""Products and skus views."""

# Django Rest Framewor
from chatbot_commerce.products.serializers.products import ProductsModelSerializer
from chatbot_commerce.products.models.departments import Department
from chatbot_commerce.stores.models.stores import StoresVtex
from django.http import Http404
from rest_framework import viewsets
from rest_framework.status import HTTP_200_OK
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema


# Serializers
from chatbot_commerce.products.serializers import StoreSerializer

# Models
from chatbot_commerce.products.models import ProductsApiVtex


class StoreViewset(viewsets.ModelViewSet):
    """Products viewset."""

    serializer_class = StoreSerializer
    lookup_field = 'name'
    allowed_methods = ['get', 'post']

    @swagger_auto_schema(
        responses={
            HTTP_200_OK: "Created"
        }
    )
    def get_serializer_class(self):
        if 'product_id' not in self.request.query_params:
            self.serializer_class = ProductsModelSerializer
        else:
            self.serializer_class = ProductsModelSerializer
        return super().get_serializer_class()

    def get_queryset(self, *args, **kwargs):
        """Restrict list to products active."""
        self.queryset = StoresVtex.objects.filter(name=self.kwargs.get('store'))
        if 'product_id' not in self.request.query_params:
            self.queryset = ProductsApiVtex.objects.filter(
                department_name__in=Department.objects.filter(
                    store=StoresVtex.objects.filter(
                        name=self.kwargs.get('store')
                    )
                    .first()
                )
            )
        else:
            self.queryset = ProductsApiVtex.objects.filter(
                department_name__in=Department.objects.filter(
                    store=StoresVtex.objects.filter(
                        name=self.kwargs.get('store')
                    )
                    .first()
                ),
                product_id=self.request.query_params.get('product_id'),
                is_active=True
            )

        return self.queryset

    def create(self, request, *args, **kwargs):
        try:
            self.get_object()
        except (Http404, AssertionError):
            data = self.serializer_class(self.queryset, many=True).data
            status = HTTP_200_OK
        return Response(data=data, status=status)

    def post(self, *args, **kwargs):
        """Restrict list to products active."""
        obj = self.get_object()
        data = self.serializer_class(obj).data
        status = HTTP_200_OK
        return Response(data=data, status=status)
