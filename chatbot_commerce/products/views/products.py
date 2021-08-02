"""Products and skus views."""

# Django Rest Framewor
from django.http import Http404
from rest_framework import viewsets
from rest_framework.status import HTTP_200_OK
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from drf_yasg.utils import swagger_auto_schema

# Django
from django.db.models.query_utils import DeferredAttribute

# Serializers
from chatbot_commerce.products.serializers import ProductsModelSerializer

# Models
from chatbot_commerce.products.models import ProductsApiVtex

# Utils
from chatbot_commerce.utils.methods.represent import parser_to_represent


class PageProducts(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'


class ProductsViewset(viewsets.ModelViewSet):
    """Products viewset."""

    serializer_class = ProductsModelSerializer
    pagination_class = PageProducts
    lookup_field = 'product_id'
    allowed_methods = ['get', 'post']

    @swagger_auto_schema(
        responses={
            HTTP_200_OK: "Created"
        }
    )
    def get_queryset(self, *args, **kwargs):
        """Restrict list to products active."""
        query_params = self.request.query_params
        not_allowed_keys = ['is_active']
        allowed_keys = [key for key, value in vars(ProductsApiVtex).items() if type(value) == DeferredAttribute]
        product_params = {key+'__in': parser_to_represent(string.split(',')) for key, string in query_params.items() if key in allowed_keys and key not in not_allowed_keys}
        self.queryset = ProductsApiVtex.objects.filter(is_active=True, **product_params)
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
