from decimal import Decimal
from django.conf import settings
from django.db import models
from products.models import Product
from orders.models import Order, OrderItem

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)

    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    def subtotal(self):
        return sum(item.get_total_price() for item in self.items.filter(is_selected=True))

    def iva(self):
        return self.subtotal() * Decimal('0.19')

    def envio(self):
        envio_base = Decimal('10000.00')
        umbral_envio_gratis = Decimal('100000.00')
        return envio_base if self.subtotal() < umbral_envio_gratis else Decimal('0.00')

    def total(self):
        return self.subtotal() + self.iva() + self.envio()

    def clear(self, only_selected=True):
        if only_selected:
            self.items.filter(is_selected=True).delete()
        else:
            self.items.all().delete()

    def checkout(self, payment_method="card"):
        order = Order.objects.create(user=self.user, payment_method=payment_method)
        for item in self.items.filter(is_selected=True):
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=Decimal(item.product.price)
            )
            item.product.stock -= item.quantity
            item.product.save()
        self.clear()
        return order

    def __str__(self):
        return f"Carrito de {self.user}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    is_selected = models.BooleanField(default=True)

    class Meta:
        unique_together = ("cart", "product")
        
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def subtotal(self):
        return self.product.price * Decimal(self.quantity)

    def get_total_price(self):
        return self.product.price * self.quantity
