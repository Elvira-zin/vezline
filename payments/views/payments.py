from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from payments.forms.payments import PaymentForm
from payments.models import Payment


def chosen_booking(form):
    """The booking being paid: for the summary card on the payment page."""
    if "booking" not in form.fields:
        return form.instance.booking

    booking_id = str(form["booking"].value() or "")
    if not booking_id.isdigit():
        return None
    return form.fields["booking"].queryset.filter(pk=booking_id).first()


class UserPaymentsMixin(LoginRequiredMixin):
    """Only the logged-in user's payments. Someone else's payment gives 404."""

    def get_queryset(self):
        return Payment.objects.filter(
            booking__user=self.request.user
        ).select_related(
            "booking__flight__departure_airport",
            "booking__flight__arrival_airport",
            "booking__seat",
        )


class PaymentFormMixin:
    """Shared by create and edit: same form, template and summary card."""

    form_class = PaymentForm
    template_name = "payments/payment_form.html"
    success_url = reverse_lazy("payment-list")

    def get_form_kwargs(self):
        # PaymentForm shows only this user's bookings, so it needs the user
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["booking"] = chosen_booking(context["form"])
        return context


class PaymentListView(UserPaymentsMixin, ListView):
    template_name = "payments/payments_list.html"
    context_object_name = "payments"

    def get_queryset(self):
        return super().get_queryset().order_by("-created_at")


class PaymentCreateView(LoginRequiredMixin, PaymentFormMixin, CreateView):
    def get_initial(self):
        # "Pay" buttons link here as ?booking=<id>
        initial = super().get_initial()
        booking_id = self.request.GET.get("booking", "")
        if booking_id.isdigit():
            initial["booking"] = booking_id
        return initial

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Payment for booking {self.object.booking.booking_number} is saved.",
        )
        return response


class PaymentUpdateView(UserPaymentsMixin, PaymentFormMixin, UpdateView):
    def form_valid(self, form):
        messages.success(self.request, "Payment updated.")
        return super().form_valid(form)


class PaymentDeleteView(UserPaymentsMixin, DeleteView):
    template_name = "payments/payment_confirm_delete.html"
    context_object_name = "payment"
    success_url = reverse_lazy("payment-list")

    def form_valid(self, form):
        messages.success(self.request, "Payment deleted.")
        return super().form_valid(form)
