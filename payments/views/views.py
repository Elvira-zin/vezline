from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from payments.forms.payments import PaymentForm
from payments.models import Payment


@login_required
def payments_list(request):
    payments = Payment.objects.filter(booking__user=request.user).select_related("booking__flight")
    return render(request, "payments/payments_list.html", {"payments": payments})


@login_required
def payment_create(request):
    if request.method == "POST":
        form = PaymentForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("payment-list")
    else:
        form = PaymentForm(user=request.user)
    return render(request, "payments/payment_form.html", {"form": form})