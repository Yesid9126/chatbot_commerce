from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models.functions import Lower
from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView, FormView, UpdateView
from django.views.generic.list import ListView

from chatbot_commerce.vehicles.filters.filters import VehicleFilter
from chatbot_commerce.vehicles.forms import VehiclesForm
from chatbot_commerce.vehicles.models.vehicles import Vehicle


class RegistrationView(FormView):
    template_name = "vehicle_registration.html"
    form_class = VehiclesForm

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "successful registration")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("vehicles:registration-vehicles")

    def form_invalid(self, form):
        # Add action to invalid form phase
        messages.warning(self.request, "Check fields")
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super(RegistrationView, self).get_context_data(**kwargs)
        brands = (
            Vehicle.objects.all()
            .order_by()
            .values_list("brand", flat=True)
            .annotate(handle_lower=Lower("brand"))
            .distinct("handle_lower")
        )
        context["brands"] = brands
        return context


class VehiclesListView(ListView):
    model = Vehicle
    template_name = "list_vehicles.html"
    context_object_name = "vehicles"
    paginate_by = 10
    # filterset_class = VehicleFilter

    def get_queryset(self):
        vehicles = Vehicle.objects.all()
        vehicles_filter = VehicleFilter(self.request.GET, queryset=vehicles)
        vehicles = vehicles_filter.qs
        return vehicles

    def get_context_data(self, **kwargs):
        context = super(VehiclesListView, self).get_context_data(**kwargs)
        vehicles = Vehicle.objects.all()
        vehicles_filter = VehicleFilter(self.request.GET, queryset=vehicles)
        brands = (
            Vehicle.objects.all()
            .order_by()
            .values_list("brand", flat=True)
            .annotate(handle_lower=Lower("brand"))
            .distinct("handle_lower")
        )
        context["brands"] = brands
        context["filter"] = vehicles_filter
        return context


class VehicleDelete(DeleteView):
    model = Vehicle
    template_name = "vehicle_delete.html"
    form_class = VehiclesForm
    success_url = reverse_lazy("vehicles:list-vehicles")
    success_message = "Eliminado Exitosamente"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(VehicleDelete, self).delete(request, *args, **kwargs)


class VehicleUpdate(UpdateView, SuccessMessageMixin):
    model = Vehicle
    template_name = "vehicle_registration.html"
    success_url = reverse_lazy("vehicles:list-vehicles")
    form_class = VehiclesForm
    success_message = "Actualizado exitosamente"

    def get_context_data(self, **kwargs):
        context = super(VehicleUpdate, self).get_context_data(**kwargs)
        brands = (
            Vehicle.objects.all()
            .order_by()
            .values_list("brand", flat=True)
            .annotate(handle_lower=Lower("brand"))
            .distinct("handle_lower")
        )
        context["brands"] = brands
        return context

    def form_invalid(self, form):
        messages.warning(self.request, "Campos no validos")
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        messages.success(self.request, self.success_message)
        return super().form_valid(form)


# when debug = False rediret if 404
# def handler404(request, *args, **kwargs):
#     return render(request, "pages-404.html")


# def handler500(request, *args, **kwargs):
#     return render(request, "pages-500.html")
