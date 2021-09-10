from chatbot_commerce.products.models import Product
from django_grpc_framework import generics
from chatbot_commerce.products.serializers import ProductProtoSerializer


class ProductService(generics.ModelService):
    queryset = Product.objects.all().order_by()
    serializer_class = ProductProtoSerializer