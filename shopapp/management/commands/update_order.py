from django.core.management import BaseCommand

from shopapp.models import Order, Product


class Command(BaseCommand):
    """
        Updated order
    """
    def handle(self, *args, **options):
        order = Order.objects.first()
        if not order:
            self.stdout.write("Not order found")
            return

        products = Product.objects.all()
        for product in products:
            order.products.add(product)

        order.save()
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully added products {order.products.all()} to order {order}."
            )
        )