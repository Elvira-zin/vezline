from django.urls import path
from payments.views.payments import payment_edit, payment_create, payments_list, payment_delete

urlpatterns = [
    path("", payments_list, name="payment-list"),
    path("create/", payment_create, name="payment-create"),
    path("<int:pk>/edit/", payment_edit, name="payment-edit"),
    path("<int:pk>/delete/", payment_delete, name="payment-delete"),
]