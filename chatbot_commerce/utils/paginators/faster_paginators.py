from django.core.paginator import Paginator
from django.utils.functional import cached_property
from rest_framework.pagination import PageNumberPagination

class FastDjangoPaginator(Paginator):
    @cached_property
    def count(self) -> int:
        return len(self.object_list.values_list('pk', flat=True))

class FasterPagenumberPagination(PageNumberPagination):
    django_paginator_class = FastDjangoPaginator