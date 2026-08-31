from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from products.models import Product
from .models import Cart, CartItem
from .forms import CartItemUpdateForm, SelectAllForm
from orders.models import Order


@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    context = {
        "cart": cart,
        "items": cart.items.all() if cart.items.exists() else [],
        "subtotal": cart.subtotal(),
        "iva": cart.iva(),
        "shipping": cart.envio(),
        "total": cart.total(),
    }
    return render(request, "cart/cart_detail.html", context)


@login_required
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={"quantity": 1})
    if not created:
        item.quantity += 1
    item.is_selected = True
    if item.quantity > product.stock:
        item.quantity = product.stock
        messages.warning(request, "Cantidad ajustada al stock disponible.")
    item.save()
    messages.success(request, f"{product.name} añadido al carrito.")
    return redirect("cart_detail")


@login_required
def cart_item_update(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart=request.user.cart)
    if request.method == "POST":
        try:
            qty = int(request.POST.get("quantity", 1))
        except ValueError:
            qty = 1

        if qty <= 0:
            return redirect("cart_remove", item_id=item.id)

        if qty > item.product.stock:
            qty = item.product.stock
            messages.warning(request, "Cantidad ajustada al stock disponible.")

        item.quantity = qty
        item.save()
        messages.success(request, "Cantidad actualizada.")
    return redirect("cart_detail")


@login_required
def cart_item_delete(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart=request.user.cart)
    item.delete()
    messages.info(request, "Producto eliminado del carrito.")
    return redirect("cart_detail")


@login_required
def cart_item_toggle_select(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart=request.user.cart)
    item.is_selected = not item.is_selected
    item.save()
    return redirect("cart_detail")


@login_required
def cart_select_all(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    form = SelectAllForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        select = form.cleaned_data["select"]
        cart.items.update(is_selected=bool(select))
    return redirect("cart_detail")


@login_required
def cart_clear(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart.clear(only_selected=False)
    messages.info(request, "Carrito vaciado.")
    return redirect("cart_detail")


@login_required
def checkout(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    if request.method == "POST":
        payment_method = request.POST.get("payment_method", "card")
        order = cart.checkout(payment_method=payment_method)
        messages.success(request, f"Pedido #{order.id} creado con éxito.")
        return redirect("order_detail", order_id=order.id)
    return render(request, "cart/checkout.html", {"cart": cart})