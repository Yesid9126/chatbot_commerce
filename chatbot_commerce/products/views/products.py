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
from django.db.models import Q

# Models
from chatbot_commerce.products.models import Product, Department, Skus, Image
from chatbot_commerce.stores.models import Store


attr_type_param = openapi.Parameter('skus__attributes__attribute_type__name', openapi.IN_QUERY, description="attr_type", type=openapi.TYPE_STRING)
attr_value_param = openapi.Parameter('skus__attributes__value', openapi.IN_QUERY, description="attr_value", type=openapi.TYPE_STRING)
total_quantity_param = openapi.Parameter('skus__total_quantity', openapi.IN_QUERY, description="quantity", type=openapi.TYPE_STRING)


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
        'sub_category__name', 'department__name', 'reference_id', 'skus__sku_name'
    )
    ordering_fields = ('created',)
    filter_fields = (
        'skus__attributes__attribute_type__name',
        'skus__attributes__value',
        'skus__total_quantity'
    )

    def dispatch(self, request, *args, **kwargs):
        slug_name = kwargs['store_slug_name']
        self.store = get_object_or_404(Store, slug_name=slug_name)

        filter_data = {key.replace('skus__', ''): value for key, value in request.GET.items() if key in ['skus__attributes__attribute_type__name', 'skus__attributes__value', 'skus__total_quantity']}
        skus = Skus.objects.filter(~Q(total_quantity=0), product__in=self.get_queryset(), is_active=True)
        skus = skus.filter(**filter_data)
        sku_pks = Image.objects.filter(sku__in=skus).values_list('sku__pk', flat=True)
        self.skus = skus.filter(Q(pk__in=sku_pks))

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Product.objects.filter(store=self.store, is_active=True)
        return queryset

    def get_serializer_context(self):
        return self.skus

    @swagger_auto_schema(manual_parameters=[attr_type_param, attr_value_param, total_quantity_param])
    def list(self, request, *args, **kwargs):
        """
        Return all products

        search = Put a keyword like name category or department to filter whith it
        example... search = jeans azul L
        """
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(skus__in=self.skus).distinct()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(manual_parameters=[attr_type_param, attr_value_param, total_quantity_param])
    def retrieve(self, request, *args, **kwargs):
        """
        Return a single department with tree category
        """
        obj = Product.objects.filter(store=self.store, skus__in=self.skus, pk=kwargs['pk']).first()
        return Response(self.get_serializer(obj).data)


class DepartmentsViewset(mixins.RetrieveModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet):

    serializer_class = DepartmentTreeModelSerializer
    lookup_field = 'department_name'
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

    def list(self, request, *args, **kwargs):
        """
        Return all departments with tree category

        search = Put a keyword like name category or department to filter whith it
        example... search = Hombres
        """
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        Return a single department with tree category
        """
        obj = Department.objects.filter(store=self.store, name=kwargs['department_name']).first()
        return Response(self.serializer_class(obj).data)
