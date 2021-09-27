"""Orders views."""


# Django Rest Framework
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404

# Serializer
from chatbot_commerce.orders.serializers import CreateOrderSerializer

# Utils
from chatbot_commerce.utils.payment_url import cart_url

# Models
from chatbot_commerce.stores.models import Store

class OrderViewSet(viewsets.GenericViewSet):
    """Web hook view set."""

    def dispatch(self, request, *args, **kwargs):
        import ipdb ; ipdb.set_trace()
        slug_name = kwargs['store_slug_name']
        self.store = get_object_or_404(Store, slug_name=slug_name)
        import ipdb ; ipdb.set_trace()
        return super().dispatch(request, *args, **kwargs)

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
        url = cart_url(list_sku)
        return Response(request.data, status=status.HTTP_200_OK)
