"""Products and skus views."""

# Django Rest Framewor
from django.http import Http404
from rest_framework import viewsets
from rest_framework.status import HTTP_200_OK
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


# Serializers
from chatbot_commerce.products.serializers import ProductsModelSerializer

# Models
from chatbot_commerce.products.models import ProductsApiVtex


class ProductsViewset(viewsets.ModelViewSet):
    """Products viewset."""

    serializer_class = ProductsModelSerializer
    lookup_field = 'product_id'
    allowed_methods = ['get', 'post']

    def get_queryset(self, *args, **kwargs):
        """Restrict list to products active."""
        self.queryset = ProductsApiVtex.objects.filter(is_active=True)
        return self.queryset

    @swagger_auto_schema(
        responses={
            HTTP_200_OK: "Created"
        }
    )

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
