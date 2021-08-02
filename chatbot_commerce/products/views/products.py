"""Product and skus views."""

# Django Rest Framework
from rest_framework.generics import get_object_or_404
from rest_framework import viewsets, mixins

# Serializers
from chatbot_commerce.products.serializers import ProductModelSerializer
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework.permissions import IsAdminUser

# Filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

# Models
from chatbot_commerce.products.models import Product
from chatbot_commerce.stores.models import Store

# Utils
from chatbot_commerce.utils.methods.represent import parser_to_represent


class ProductViewset(mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    """Product viewset."""

    serializer_class = ProductModelSerializer
    lookup_field = 'pk'
    permission_classes = [HasAPIKey | IsAdminUser]
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ('name', 'department_name')
    # ordering_fields = ('createld', 'block_status__reason', 'cto_status__name', 'cto_building',
    #                    'quickly_installation', 'detail', 'code', 'cto_technology')
    # filter_fields = ('code', 'cto_status__slug_name')

    def dispatch(self, request, *args, **kwargs):
        slug_name = kwargs['store_slug_name']
        self.store = get_object_or_404(Store, slug_name=slug_name)
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = Product.objects.all()
        return queryset
