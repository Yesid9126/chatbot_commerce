"""Product and skus views."""

# Django Rest Framework
from chatbot_commerce.products.models.skus import Attribute, AttributeType, Price
from chatbot_commerce.products.models.products import Brand
from rest_framework.generics import get_object_or_404
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

# Serializers
from chatbot_commerce.products.serializers import (ProductModelSerializer,
                                                   DepartmentTreeModelSerializer,
                                                   BrandsModelSerializer,
                                                   AttributeTypeModelSerializer)
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
sku_name_param = openapi.Parameter('skus__sku_name', openapi.IN_QUERY, description="sku_name", type=openapi.TYPE_STRING)


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
        'sub_category__name', 'department__name'
    )
    ordering_fields = ('created',)

    def dispatch(self, request, *args, **kwargs):
        slug_name = kwargs['store_slug_name']
        self.store = get_object_or_404(Store, slug_name=slug_name)
        self.queryset = Product.objects.filter(store=self.store).order_by()
        if self.store.apply_filter_enable_products:
            self.queryset = self.queryset.filter(is_active=True)

        filter_data = {key.removeprefix('skus__')+'__icontains': value for key, value in request.GET.items() if key in ['skus__attributes__attribute_type__name', 'skus__attributes__value', 'skus__sku_name']}
        skus = Skus.objects.filter(product__pk__in=self.queryset.values_list('pk', flat=True), **filter_data).order_by()
        if self.store.apply_filter_enable_skus:
            skus = skus.filter(total_quantity__gt=0, is_active=True)
        if self.store.apply_filter_image:
            sku_pks_images = Image.objects.filter(sku__pk__in=skus.values_list('pk', flat=True)).order_by().values_list('sku__pk', flat=True)
            skus = skus.filter(pk__in=sku_pks_images)
        if self.store.apply_filter_price:
            sku_pks_prices = Price.objects.filter(Q(~Q(base_price=None) & ~Q(base_price=0)), sku__pk__in=skus.values_list('pk', flat=True)).order_by().values_list('sku__pk', flat=True)
            skus = skus.filter(pk__in=sku_pks_prices)
        self.skus = skus
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.queryset

    def get_serializer_context(self):
        return self.skus

    @swagger_auto_schema(manual_parameters=[sku_name_param, attr_type_param, attr_value_param])
    def list(self, request, *args, **kwargs):
        """
        Return all products

        search = Put a keyword like name category or department to filter whith it
        example... search = jeans azul L
        """
        queryset = self.filter_queryset(self.queryset)
        if self.store.apply_filter_enable_products:
            queryset = queryset.filter(skus__pk__in=self.skus.values_list('pk', flat=True)).distinct()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_data = self.get_paginated_response(serializer.data).data
            paginated_data.pop('count')
            response = {'num_produts': self.queryset.count(), 'num_skus': self.skus.count()} | paginated_data
            return Response(data=response, status=HTTP_200_OK)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(manual_parameters=[sku_name_param, attr_type_param, attr_value_param])
    def retrieve(self, request, *args, **kwargs):
        """
        Return a single department with tree category.

        Parameters.
        """
        obj = Product.objects.filter(store=self.store, skus__pk__in=self.skus.values_list('pk', flat=True), pk=kwargs['pk']).order_by().first()
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

        for search Put a keyword like name category or department to filter whith it
        example... search = Hombres
        """
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        Return a single department with tree category.

        Parameters.
        """
        obj = Department.objects.filter(store=self.store, name=kwargs['department_name']).first()
        return Response(self.serializer_class(obj).data)


class BrandsViewset(mixins.RetrieveModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):

    serializer_class = BrandsModelSerializer
    lookup_field = 'name'
    permission_classes = [HasAPIKey | IsAdminUser]
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ('name', 'title')

    def dispatch(self, request, *args, **kwargs):
        slug_name = kwargs['store_slug_name']
        self.store = get_object_or_404(Store, slug_name=slug_name)
        self.queryset = Brand.objects.filter(store=self.store).order_by()
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.queryset

    def list(self, request, *args, **kwargs):
        """
        Return all brands of a store.

        Parameters.
        """
        queryset = self.filter_queryset(self.queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = [name for array in serializer.data for key, name in array.items() if key == 'name']
            paginated_data = self.get_paginated_response(data).data
            paginated_data['brands'] = paginated_data.pop('results')
            return Response(data=paginated_data, status=HTTP_200_OK)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """
        Return a single brand with tree category.

        Parameters.
        """
        obj = Brand.objects.filter(store=self.store, name=kwargs['name']).first()
        return Response(self.serializer_class(obj).data)


class AttributesViewset(mixins.ListModelMixin,
                        viewsets.GenericViewSet):

    serializer_class = AttributeTypeModelSerializer
    permission_classes = [HasAPIKey | IsAdminUser]
    filter_backends = (DjangoFilterBackend,)

    def dispatch(self, request, *args, **kwargs):
        slug_name = kwargs['store_slug_name']
        self.store = get_object_or_404(Store, slug_name=slug_name)
        self.attributes = Attribute.objects.filter(attribute_type__in=self.get_queryset())
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = AttributeType.objects.filter(store=self.store)
        return queryset

    def get_serializer_context(self):
        return self.attributes

    def list(self, request, *args, **kwargs):
        """
        Return all attribute of a type.

        Parameters.
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = {key: array for array in serializer.data for key, array in array.items()}
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
