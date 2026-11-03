from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

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


@login_required
def payments_list(request):
    payments = Payment.objects.filter(
        booking__user=request.user
    ).select_related(
        "booking__flight__departure_airport",
        "booking__flight__arrival_airport",
    ).order_by("-created_at")
    return render(request, "payments/payments_list.html", {"payments": payments})


@login_required
def payment_create(request):
    if request.method == "POST":
        form = PaymentForm(request.POST, user=request.user)
        if form.is_valid():
            payment = form.save()
            messages.success(request, f"Payment for booking {payment.booking.booking_number} is saved.")
            return redirect("payment-list")
    else:
        # "Pay" buttons link here as ?booking=<id>
        form = PaymentForm(user=request.user, initial={"booking": request.GET.get("booking")})

    return render(
        request,
        "payments/payment_form.html",
        {"form": form, "booking": chosen_booking(form)},
    )


@login_required
def payment_edit(request, pk):
    payment = get_object_or_404(Payment, pk=pk, booking__user=request.user)

    if request.method == "POST":
        form = PaymentForm(request.POST, user=request.user, instance=payment)

        if form.is_valid():
            form.save()
            messages.success(request, "Payment updated.")
            return redirect("payment-list")
    else:
        form = PaymentForm(user=request.user, instance=payment)

    return render(
        request,
        "payments/payment_form.html",
        {"form": form, "booking": chosen_booking(form)},
    )


@login_required
def payment_delete(request, pk):
    payment = get_object_or_404(Payment, pk=pk, booking__user=request.user)

    if request.method == "POST":
        payment.delete()
        messages.success(request, "Payment deleted.")
        return redirect("payment-list")

    return render(
        request,
        "payments/payment_confirm_delete.html",
        {"payment": payment},
    )
