from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from orders.models import Order
from .forms import ProfileForm
import re

User = get_user_model() 

def register(request):
    if request.method == "POST":
        username = request.POST.get("username").strip()
        email = request.POST.get("email").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if not username or not email or not password1 or not password2:
            messages.error(request, "Todos los campos son obligatorios.")
        elif password1 != password2:
            messages.error(request, "Las contraseñas no coinciden.")
        elif len(password1) < 8:
            messages.error(request, "La contraseña debe tener al menos 8 caracteres.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "El usuario ya existe.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Ya existe una cuenta con este correo electrónico.")
        elif not re.search(r'\d', password1) or not re.search(r'[A-Za-z]', password1):
            messages.error(request, "La contraseña debe contener letras y números.")
        else:
            user = User.objects.create_user(username=username, email=email, password=password1, first_name=first_name, last_name=last_name)
            user.save()
            messages.success(request, "¡Cuenta creada correctamente!")
            return redirect("login")

    return render(request, "autentication/register.html")


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Bienvenido {username}!")
                return redirect("product_list") 
            else:
                messages.error(request, "Usuario o contraseña incorrectos")
        else:
            messages.error(request, "Usuario o contraseña incorrectos")
    else:
        form = AuthenticationForm()
    return render(request, "autentication/login.html", {"form": form})

def logout_view(request):
    logout(request) 
    messages.success(request, "Has cerrado sesión correctamente.")
    return redirect("product_list")  

@login_required
def profile_view(request):
    messages.get_messages(request)
    orders = request.user.orders.order_by('-created_at')
    return render(request, 'autentication/profile.html', {"orders": orders})

@login_required
def profile_edit(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect("profile_view")
    else:
        form = ProfileForm(instance=request.user)

    return render(request, "autentication/profile_edit.html", {"form": form})

class CustomPasswordChangeView(PasswordChangeView):
    def form_valid(self, form):
        messages.success(self.request, "Contraseña cambiada con éxito.")
        return super().form_valid(form)