from django.db import models
from users.models import User
from products.models import Product

class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pendiente"),
        ("paid", "Pagado"),
        ("shipped", "Enviado"),
        ("completed", "Completado"),
        ("canceled", "Cancelado"),
    ]
    PAYMENT_CHOICES = [
        ("card", "Tarjeta"),
        ("pse", "PSE"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    metodo_pago = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default="card")

    nombre = models.CharField(max_length=50, blank=True)
    apellido = models.CharField(max_length=50, blank=True)
    dirección = models.CharField(max_length=255, blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    telefono = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return f"Pedido #{self.id} - {self.user.username}"

    def calculate_total(self):
        return sum(item.subtotal() for item in self.items.all())

    def save(self, *args, **kwargs):
        if self.pk:
            self.total_amount = self.calculate_total()
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name if self.product else 'Producto eliminado'}"

    def subtotal(self):
        return self.price * self.quantity
