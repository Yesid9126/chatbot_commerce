"""Orders views."""


# Django Rest Framework
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

# Serializer
from chatbot_commerce.orders.serializers import CreateOrderSerializer

# Utils
from chatbot_commerce.utils.payment_url import kart_url

# Models
from chatbot_commerce.stores.models import Store

class OrderViewSet(viewsets.GenericViewSet):
    """Web hook view set."""


    def get_serializer_class(self):
        """Return serializer based on action."""
        if self.action == 'create_order':
            return CreateOrderSerializer

    @action(detail=False, methods=['post'])
    def create_order(self, request):
        """Endpoint order management."""
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = request.data
        list_sku = data['sku_ids']
        store = Store.objects.filter(slug_name=data.get('store')).get()
        url = kart_url(store, list_sku)
        return Response(request.data, status=status.HTTP_200_OK)
