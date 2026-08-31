from django.urls import path, reverse_lazy
from . import views
from .views import profile_edit, profile_view
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/', profile_view, name='profile_view'),
    path('perfil/editar/', profile_edit, name='profile_edit'),    
    path('password/change/', auth_views.PasswordChangeView.as_view(
        template_name='autentication/password_change.html',
        success_url=reverse_lazy('profile_view')
    ), name='password_change'),
]
