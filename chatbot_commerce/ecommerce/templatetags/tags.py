import re

from django import template

from chatbot_commerce.orders.models.orders import Order

register = template.Library()


# as per recommendation from @freylis, compile once only
CLEANR = re.compile("<.*?>")


@register.filter
def replace1(value):

    value = value.replace("<ul>", " ")
    value = value.replace("</ul>", " ")
    value = value.replace("<li>", " ")
    value = value.replace("</li>", ",")
    value = value.replace("<p>", "")
    value = value.replace("</p>", ". \n")

    value = value.replace("&aacute;", "á")
    value = value.replace("&eacute;", "é")
    value = value.replace("&iacute;", "í")
    value = value.replace("&oacute;", "ó")
    value = value.replace("&uacute;", "ú")
    print(value)

    value = re.sub(CLEANR, "", value)
    # import ipdb;ipdb.set_trace()
    i = -1
    x = 0
    while x == 0:
        if value[i] != " ":
            if not value.endswith("."):
                value += "."
            x = 1
        i -= 1
        if i < -10:
            x = 1
    return value


@register.filter
def count_items(request):
    session_number = request.session.get("session_number", False)
    if session_number:
        queryset = Order.objects.filter(customer=session_number)
        if queryset.exists():
            return queryset[0].item.count()
    return 0
