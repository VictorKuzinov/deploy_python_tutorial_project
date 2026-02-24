from collections.abc import Sequence

from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db import transaction

from shopapp.models import Order, Product


class Command(BaseCommand):
    """
        Creates order
    """
    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Create order with products")
        user = User.objects.get(username="admin")
        product: Sequence[Product] = Product.objects.all()
        order, created = Order.objects.get_or_create(
            delivery_address = "Lenina Prospekt, 2, 22, Yekaterinburg, Sverdlovsk Oblast, Russia,",
            promocode = "SALE5936",
            user = user,
        )
        for product in product:
            order.products.add(product)
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created order {order.pk}" ))
        else:
            self.stdout.write(self.style.WARNING(f"This order has already been created {order.pk}"))
