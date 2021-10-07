from django.core.paginator import Paginator
from django.utils.functional import cached_property
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class FastDjangoPaginator(Paginator):
    @cached_property
    def count(self) -> int:
        return len(self.object_list.values_list('pk', flat=True))


class FasterPagenumberPagination(PageNumberPagination):
    django_paginator_class = FastDjangoPaginator

    def get_paginated_response(self, data):
        return Response(
            {
                'count': self.page.paginator.count,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'results': data
            }
        )
