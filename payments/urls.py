from django.urls import path

from payments.views.payments import (
    PaymentListView,
    PaymentCreateView,
    PaymentUpdateView,
    PaymentDeleteView,
)

urlpatterns = [
    path("", PaymentListView.as_view(), name="payment-list"),
    path("create/", PaymentCreateView.as_view(), name="payment-create"),
    path("<int:pk>/edit/", PaymentUpdateView.as_view(), name="payment-edit"),
    path("<int:pk>/delete/", PaymentDeleteView.as_view(), name="payment-delete"),
]
