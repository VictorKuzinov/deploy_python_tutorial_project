from django.core.management import BaseCommand
from django.db.models import Sum, Count

from shopapp.models import Order


class Command(BaseCommand):
    """
        Demo annotations
    """

    def handle(self, *args, **options):
        self.stdout.write("Start demo annotations")
        orders  = Order.objects.annotate(
            total = Sum('products__price', default=0),
            product_count = Count("products")
        )
        for order in orders:
            print(f"Order: {order.id} "
                  f"with {order.product_count} products "
                  f"product worth: {order.total} ")

        self.stdout.write(self.style.SUCCESS("Done..." ))
