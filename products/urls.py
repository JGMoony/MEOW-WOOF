from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('<int:pk>/', views.product_detail, name='product_detail'),
    path('categoria/<slug:slug>', views.category_view, name='category'),
    path('<int:pk>/review/edit/', views.review_edit, name='review_edit'),
    path('<int:pk>/review/delete/', views.review_delete, name='review_delete'),
    path("new/", views.product_create, name="product_create"),
    path("<int:pk>/edit/", views.product_update, name="product_update"),
    path("<int:pk>/delete/", views.product_delete, name="product_delete"),
    path('producto/<int:pk>/eliminar/', views.ProductDeleteView.as_view(), name='product_delete'),
]