from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db.models import Avg, Min, Max, Count

from shopapp.models import Product


class Command(BaseCommand):
    """
        Demo aggregations
    """

    def handle(self, *args, **options):
        self.stdout.write("Start demo aggregations")


        result = Product.objects.filter(
            name__contains='Smartphone'
        ).aggregate(
            Avg('price'),
            Min('price'),
            max = Max('price'),
            count = Count('price'),
        )

        print(result)

        self.stdout.write(self.style.SUCCESS("Done..." ))
