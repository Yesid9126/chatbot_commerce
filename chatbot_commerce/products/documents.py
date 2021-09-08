from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry
from .models import Product

@registry.register_document
class ProductDocument(Document):
    class Index:
        # Name of the Elasticsearch index
        name = 'Products'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    class Django:
        model = Product

        fields = [
            'id',
            'external_id',
            'name',
            'keywords',
            'title',
            'is_active',
        ]
