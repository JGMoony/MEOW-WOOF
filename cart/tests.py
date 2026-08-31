from django.test import TestCase
from django.contrib.auth import get_user_model
from products.models import Product, Category
from .models import CartItem

User = get_user_model()

class CartFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u", password="p")
        self.client.login(username="u", password="p")
        cat = Category.objects.create(name="Juguetes")
        self.prod = Product.objects.create(name="Pelota", description="x", price=10000, stock=5, category=cat)

    def test_add_and_checkout(self):
        r = self.client.get(f"/cart/add/{self.prod.id}/")
        self.assertEqual(CartItem.objects.count(), 1)