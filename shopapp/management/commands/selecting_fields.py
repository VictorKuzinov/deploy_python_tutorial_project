from django.contrib.auth.models import User
from django.core.management import BaseCommand

from shopapp.models import Product


class Command(BaseCommand):
    """
        Demo select fields
    """

    def handle(self, *args, **options):
        self.stdout.write("Start demo select fields")
        products_values = Product.objects.values('pk', 'name')
        users_info = User.objects.values_list('username', flat=True)
        print(list(users_info))
        for product in products_values:
            print(product)

        for user in users_info:
            print(user)

        self.stdout.write(self.style.SUCCESS("Done..." ))
