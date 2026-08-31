from django.urls import path
from .views import dashboard_data, dashboard_view

urlpatterns = [
    path("", dashboard_view, name="dashboard"),
    path("data/", dashboard_data, name="dashboard_data"),
]