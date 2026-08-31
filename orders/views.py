from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render, get_object_or_404
from cart.models import CartItem
from products.models import Product
from .models import Order, OrderItem
from .forms import CheckoutForm

@login_required
def checkout_view(request):
    cart = request.user.cart
    selected = cart.items.select_related("product").filter(is_selected=True)
    if not selected.exists():
        messages.error(request, "No hay productos seleccionados para comprar.")
        return redirect("cart_detail")

    subtotal = sum(i.subtotal() for i in selected)
    iva = subtotal * Decimal('0.19')
    envio = 0
    total = subtotal + iva + envio

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            request.session["checkout"] = {
                "nombre": form.cleaned_data["nombre"],
                "apellido": form.cleaned_data["apellido"],
                "dirección": form.cleaned_data["dirección"],
                "ciudad": form.cleaned_data["ciudad"],
                "telefono": form.cleaned_data["telefono"],
                "metodo_pago": form.cleaned_data["metodo_pago"],
                "subtotal": str(subtotal),
                "iva": str(iva),
                "envio": str(envio),
                "total": str(total),
            }
            return redirect("checkout_confirm")
    else:
        form = CheckoutForm()

    return render(request, "orders/checkout.html", {
        "items": selected,
        "subtotal": subtotal,
        "iva": iva,
        "envio": envio,
        "total": total,
        "form": form
    })

@login_required
def checkout_confirm(request):
    cart = request.user.cart
    selected = cart.items.select_related("product").filter(is_selected=True)
    data = request.session.get("checkout")

    if not selected.exists() or not data:
        messages.error(request, "Sesión de checkout inválida.")
        return redirect("cart_detail")

    if request.method == "POST":
        with transaction.atomic():
            product_ids = [i.product_id for i in selected]
            locked = list(Product.objects.select_for_update().filter(id__in=product_ids))

            for item in selected:
                if item.quantity > item.product.stock:
                    messages.error(request, f"Stock insuficiente para {item.product.name}.")
                    return redirect("cart_detail")

            order = Order.objects.create(
                user=request.user,
                nombre=data["nombre"],
                apellido=data["apellido"],
                dirección=data["dirección"],
                ciudad=data["ciudad"],
                telefono=data["telefono"],
                metodo_pago=data["metodo_pago"],
                status="pending",
            )
            print(f"Orden creada: {order.id}")

            for item in selected:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price,
                )
                item.product.stock -= item.quantity
                item.product.save()

            order.total_amount = order.calculate_total()
            order.save()

            cart.clear(only_selected=True)

        request.session.pop("checkout", None)
        messages.success(request, f"Compra realizada. Pedido #{order.id}")
        return redirect("order_success", order_id=order.id)

    subtotal = sum(i.subtotal() for i in selected)
    iva = subtotal * Decimal('0.19')
    envio = 0
    total = subtotal + iva + envio

    return render(request, "orders/checkout_confirm.html", {
        "items": selected,
        "subtotal": subtotal,
        "iva": iva,
        "envio": envio,
        "total": total,
        "data": data
    })

@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "orders/order_success.html", {"order": order})


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {"orders": orders})
