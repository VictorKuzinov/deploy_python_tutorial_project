from django.contrib.auth.models import User
from django.core.management import BaseCommand

from shopapp.models import Product


class Command(BaseCommand):
    """
        Demo balk actions
    """

    def handle(self, *args, **options):
        self.stdout.write("Start demo bulk actions")
        # info = [
        #     {"Smartphone_1", 199.99},
        #     {"Smartphone_2", 299.99},
        #     {"Smartphone_3", 399.99},
        # ]
        # products = [
        #     Product(name=name, price=price)
        #     for name, price in info
        # ]
        # result = Product.objects.bulk_create(products)
        # for obj in result:
        #     print(obj)

        result = Product.objects.filter(
            name__contains ='Smartphone',
        ).update(discount=15)

        print(result)

        self.stdout.write(self.style.SUCCESS("Done..." ))
