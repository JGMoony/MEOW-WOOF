from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('update/<int:item_id>/', views.cart_item_update, name='cart_update'),
    path('remove/<int:item_id>/', views.cart_item_delete, name='cart_remove'),
    path('clear/', views.cart_clear, name='cart_clear'),
    path('checkout/', views.checkout, name='checkout'),
]