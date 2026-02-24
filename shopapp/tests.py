from itertools import product
from random import choices
from string import ascii_letters

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.conf import settings

from .models import Product
from .utils import add_two_numbers

class AddTwoNumbersTestCase(TestCase):
    def test_add_two_numbers(self):
        result = add_two_numbers(1, 2)
        self.assertEqual(result, 3)


class ProductCreateViewTestCase(TestCase):
    def setUp(self)->None:
        self.product_name = "".join(choices(ascii_letters, k=10))
        Product.objects.filter(name=self.product_name).delete()

    def test_product_create_view(self):
        respose = self.client.post(
            reverse("shopapp:product_create"),
            {
                "name": self.product_name,
                "price": "1234.45",
                "description": "A good table!",
                "discount": "10",

            }
        )
        self.assertRedirects(respose, reverse("shopapp:products_list"))
        self.assertTrue(Product.objects.filter(name=self.product_name).exists())


class ProductDetailViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls)->None:
        name = "".join(choices(ascii_letters, k=10))
        cls.product = Product.objects.create(name=name)

    @classmethod
    def tearDownClass(cls)->None:
        cls.product.delete()

    def test_get_product(self):
        response = self.client.get(
            reverse("shopapp:product_details",
                    kwargs={"pk": self.product.pk})
        )
        self.assertEqual(response.status_code, 200)


    def test_get_product_and_content(self):
        response = self.client.get(
            reverse("shopapp:product_details",
                    kwargs={"pk": self.product.pk})
        )
        self.assertContains(response, self.product.name)

class ProductsListViewTestCase(TestCase):
    fixtures = [
        "products-fixture.json",
    ]
    def test_products_list(self):
        response = self.client.get(reverse("shopapp:products_list"))
        self.assertQuerySetEqual(
            qs = Product.objects.filter(archived=False).all(),
            values = (p.pk for p in response.context["products"]),
            transform = lambda p: p.pk
        )
        self.assertTemplateUsed(response, "shopapp/products-list.html")


class OrdersListViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username="Bob_test", password="qwerty")

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self)->None:
        self.client.force_login(self.user)

    def test_order_view(self):
        response = self.client.get(reverse("shopapp:orders_list"))
        self.assertContains(response, "Orders")

    def test_order_view_not_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse("shopapp:orders_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL),response.url)

class ProductsExportViewTestCase(TestCase):
    fixtures = [
        "products-fixture.json",
    ]
    def test_get_products_view(self):
        response = self.client.get(
            reverse("shopapp:products-export"),
        )
        self.assertEqual(response.status_code, 200)
        products = Product.objects.order_by("pk").all()
        expected_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "price": str(product.price),
                "archived": product.archived,
            }
            for product in products
        ]
        products_data = response.json()
        self.assertEqual(products_data['products'],
                             expected_data
                             )
