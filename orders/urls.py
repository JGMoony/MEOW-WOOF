from django.urls import path
from . import views

urlpatterns = [
    path("checkout/", views.checkout_view, name="checkout"),
    path("confirm/", views.checkout_confirm, name="checkout_confirm"),
    path("<int:order_id>/success/", views.order_success, name="order_success"),
    path('', views.order_list, name='order_list')
]