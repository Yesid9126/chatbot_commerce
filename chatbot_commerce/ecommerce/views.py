from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView
from django.views.generic.base import View

from chatbot_commerce.ecommerce.utils import random_session_id
from chatbot_commerce.orders.models import Order, OrderItem
from chatbot_commerce.products.models.skus import Skus
from chatbot_commerce.stores.models.stores import Store

# Create your views here.


class HomeView(ListView):
    model = Skus
    template_name = "home.html"
    paginate_by = 16

    def get_queryset(self):
        skus = Skus.objects.filter(product__store__name=self.kwargs["store"])
        return skus

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context["store"] = self.kwargs["store"]
        return context


class StoreListView(ListView):
    model = Store
    template_name = "stores.html"


class ProductDetailView(DetailView):
    model = Skus
    template_name = "product.html"
    slug_field = "external_id"
    slug_url_kwarg = "external_id"

    def get_queryset(self):
        skus = Skus.objects.filter(product__store__name=self.kwargs["store"])
        return skus

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        context["store"] = self.kwargs["store"]
        return context


class OrderListView(View):
    # slug_field = 'external_id'
    # slug_url_kwarg = 'external_id'

    def get(self, request, *args, **kwargs):
        session_number = self.request.session.get("session_number", random_session_id())
        # import ipdb; ipdb.set_trace()
        order_qs = Order.objects.filter(
            customer=session_number, store__name=self.kwargs["store"]
        )

        if order_qs.exists():
            order = order_qs[0]
            context = {"order": order, "store": self.kwargs["store"]}
            return render(request, "order-list.html", context)
        else:
            messages.info(request, "The Cart is empty")
            return redirect("ecommerce:home", store=self.kwargs["store"])


def add_to_car(request, external_id, store, *args, **kwargs):
    # import ipdb; ipdb.set_trace()
    item = get_object_or_404(Skus, external_id=external_id, product__store__name=store)

    session_number = request.session.get("session_number", random_session_id())
    request.session["session_number"] = session_number
    store = get_object_or_404(Store, name=store)

    order, created1 = Order.objects.get_or_create(customer=session_number, store=store)
    order_item, created2 = OrderItem.objects.get_or_create(sku_unit=item, order=order)

    # if Order.objects.filter(item=order_item, customer=session_number ):
    if created2:
        order_item.quantity = "1"

        if order_item.sku_unit.serializer_data["price"] is not None:
            order_item.price = order_item.sku_unit.serializer_data["price"][
                "base_price"
            ]

        elif order_item.sku_unit.price_set.all().first() is not None:
            order_item.price = order_item.sku_unit.price_set.all().first().base_price
        # else:
        #     order_item.price = None
        order_item.save()
        messages.info(request, "This item cuantity was added")
    else:
        quantity = int(order_item.quantity)
        quantity += 1
        order_item.quantity = str(quantity)

        if order_item.sku_unit.serializer_data["price"] is not None:
            price_aux = order_item.sku_unit.serializer_data["price"]["base_price"]
            total = price_aux * quantity
            order_item.price = total
        elif order_item.sku_unit.price_set.all().first() is not None:
            price = order_item.sku_unit.price_set.all().first().base_price
            total = price * quantity
            order_item.price = total

        order_item.save()
        messages.info(request, "This item cuantity was updated")
    # return redirect("ecommerce:order-list" )
    return redirect("ecommerce:order-list", store=store)


def remove_one_from_cart(request, external_id, store, *args, **kwargs):
    item = get_object_or_404(Skus, external_id=external_id, product__store__name=store)
    session_number = request.session.get("session_number", random_session_id())
    request.session["session_number"] = session_number
    store = get_object_or_404(Store, name=store)

    order_qs = Order.objects.filter(customer=session_number, store=store)
    if order_qs.exists():
        order = order_qs[0]
        if order.item.filter(sku_unit__external_id=external_id):
            order_item = OrderItem.objects.filter(sku_unit=item, order=order)[0]
            if int(order_item.quantity) > 1:
                quantity = int(order_item.quantity)
                quantity -= 1
                order_item.quantity = quantity
                order_item.save()
                # import ipdb; ipdb.set_trace()
            else:
                order_item.delete()
            messages.info(request, "This item quantity was update from your cart")
            return redirect("ecommerce:order-list", store=store.name)

    messages.info(request, "This item was not in your cart")
    return redirect("ecommerce:product", store=store.name, external_id=external_id)


def remove_from_cart(request, external_id, store, *args, **kwargs):
    item = get_object_or_404(Skus, external_id=external_id, product__store__name=store)
    session_number = request.session.get("session_number", random_session_id())
    request.session["session_number"] = session_number
    store = get_object_or_404(Store, name=store)

    order_qs = Order.objects.filter(customer=session_number, store=store)
    if order_qs.exists():
        order = order_qs[0]
        if order.item.filter(sku_unit__external_id=external_id):
            order_item = OrderItem.objects.filter(sku_unit=item, order=order)[0]
            order_item.delete()
            messages.info(request, "This item  was delete from your cart")
            return redirect("ecommerce:order-list", store=store.name)

    messages.info(request, "This item was not in your cart")
    return redirect("ecommerce:product", store=store.name, external_id=external_id)
