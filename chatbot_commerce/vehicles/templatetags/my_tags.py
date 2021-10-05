from django import template

register = template.Library()


@register.simple_tag
def my_url(request, value):
    d = request.GET.copy()
    d["page"] = value
    return d.urlencode()
