"""Products and skus views."""

# Django Rest Framewor
from django.db.models.fields import SlugField
from rest_framework import viewsets
from rest_framework.decorators import action

# Serializers
from chatbot_commerce.products.serializers import ProductsModelSerializer

# Models
from chatbot_commerce.products.models import ProductsApiVtex



class ProductsViewset(viewsets.ModelViewSet):
    """Products viewset."""

    serializer_class = ProductsModelSerializer
    lookup_field = 'product_id'
    @action(detail=True, methods=['get', 'post'])
    def get_queryset(self):
        """Restrict list to products active."""
        queryset = ProductsApiVtex.objects.filter(is_active=True)
        return queryset
    