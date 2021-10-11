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


def page_url(page: int, base_url: str, differ: int):
    next_page = page + 1
    if differ > -1:
        next_link = None
    elif f'page={page}' in base_url:
        next_link = base_url.replace(f'page={page}', f'page={next_page}')
    elif '?' in base_url:
        next_link = base_url.replace('?', f'?page={next_page}&')
    else:
        next_link = '?'.join((base_url, f'page={next_page}',))
    # if self.previous_page > 0:
    previous_page = page - 1
    if page < 2:
        previous_link = None
    elif f'page={page}' in base_url:
        previous_link = base_url.replace(f'page={page}', f'page={previous_page}')
    elif '?' in base_url:
        previous_link = base_url.replace('?', f'?page={previous_page}&')
    else:
        previous_link = '/?'.join((base_url, f'page={previous_page}',))
    return next_link, previous_link
