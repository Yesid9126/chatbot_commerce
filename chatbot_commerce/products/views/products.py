"""Product and skus views."""

# Django Rest Framework
from rest_framework.generics import get_object_or_404
from rest_framework import viewsets, mixins
from rest_framework.response import Response


# Serializers
from chatbot_commerce.products.serializers import ProductModelSerializer, DepartmentTreeModelSerializer
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework.permissions import IsAdminUser

# Filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
# Models
from chatbot_commerce.products.models import Product, Department
from chatbot_commerce.stores.models import Store


test_param = openapi.Parameter('skus__attributes__attribute_type__name', openapi.IN_QUERY, description="attr_type", type=openapi.TYPE_STRING)


class ProductViewset(mixins.RetrieveModelMixin,
                     mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    """Product viewset."""

    serializer_class = ProductModelSerializer
    lookup_field = 'pk'
    permission_classes = [HasAPIKey | IsAdminUser]
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = (
        'name', 'brand__name', 'keywords', 'category__name',
        'sub_category__name', 'department__name', 'reference_id',
        'skus__attributes__value'
    )
    ordering_fields = ('created',)
    filter_fields = (
        'brand__name',
        'category__name',
        'sub_category__name',
        'department__name',
        'skus__attributes__attribute_type__name'
        'skus__attributes__attribute_value'
    )

    def dispatch(self, request, *args, **kwargs):
        slug_name = kwargs['store_slug_name']
        self.store = get_object_or_404(Store, slug_name=slug_name)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Product.objects.filter(store=self.store)
        return queryset

    @swagger_auto_schema(manual_parameters=[test_param])
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class DepartmentsViewset(mixins.RetrieveModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet):

    serializer_class = DepartmentTreeModelSerializer
    lookup_field = 'pk'
    permission_classes = [HasAPIKey | IsAdminUser]
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ('name', 'categories__name', 'categories__subcategories__name')
    filter_fields = ('categories__name', 'categories__subcategories__name')

    def dispatch(self, request, *args, **kwargs):
        slug_name = kwargs['store_slug_name']
        self.store = get_object_or_404(Store, slug_name=slug_name)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Department.objects.filter(store=self.store)
        return queryset
