from django.contrib.auth.models import User
from django.db import models
from django.db.models import ForeignKey, CASCADE


def product_preview_directory_path(instance: "Product", filename: str) -> str:
    """
    Формирует путь для загрузки превью-изображения товара.

    Файл сохраняется в директорию, привязанную к конкретному товару.

    :param instance: экземпляр модели Product
    :param filename: исходное имя загружаемого файла
    :return: относительный путь для сохранения превью
    """
    return "products/product_{pk}/preview/{filename}".format(
        pk=instance.pk,
        filename=filename,
    )


class Product(models.Model):
    """
    Модель товара (Product).

    Хранит основную информацию о товаре:
    - название и описание,
    - цену и скидку,
    - превью-изображение,
    - признак архивности (мягкое удаление),
    - дату создания.

    Заказы тут: :model:`shopapp.Order`
    """

    class Meta:
        """
        Метаданные модели Product.

        По умолчанию товары сортируются по имени и цене.
        """
        ordering = ["name", "price"]

    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(null=False, blank=True, db_index=True)
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    discount = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    archived = models.BooleanField(default=False)
    preview = models.ImageField(
        null=True,
        blank=True,
        upload_to=product_preview_directory_path,
    )

    def description_short(self) -> str:
        """
        Возвращает сокращённое описание товара.

        Если длина описания превышает 40 символов,
        строка обрезается и дополняется многоточием.

        :return: сокращённое описание
        """
        if len(self.description) > 40:
            return self.description[:40] + "..."
        return self.description

    def __str__(self):
        """
        Строковое представление товара.

        Используется для отображения в админке, логах и отладке.

        :return: строка вида "Product(pk=..., name='...')"
        """
        return f"Product(pk={self.pk}, name={self.name!r})"


def product_images_directory_path(instance: "ProductImage", filename: str) -> str:
    """
    Формирует путь для загрузки дополнительных изображений товара.

    Изображения сохраняются в директории конкретного товара.

    :param instance: экземпляр модели ProductImage
    :param filename: исходное имя загружаемого файла
    :return: относительный путь для сохранения изображения
    """
    return "products/product_{pk}/images/{filename}".format(
        pk=instance.product.pk,
        filename=filename,
    )


class ProductImage(models.Model):
    """
    Модель дополнительного изображения товара (ProductImage).

    Каждое изображение связано с конкретным товаром.
    """

    product = models.ForeignKey(
        Product,
        on_delete=CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to=product_images_directory_path)
    description = models.CharField(max_length=200, null=False, blank=True)


class Order(models.Model):
    """
    Модель заказа (Order).

    Хранит:
    - адрес доставки,
    - промокод,
    - дату создания,
    - пользователя (кто сделал заказ),
    - товары в заказе (Many-to-Many),
    - файл(ы) подтверждения/чека (receipt), если есть.
    """

    delivery_address = models.TextField(null=True, blank=True)
    promocode = models.CharField(max_length=20, null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = ForeignKey(User, on_delete=models.PROTECT)
    products = models.ManyToManyField(Product, related_name="orders")
    receipt = models.FileField(null=True, upload_to="orders/receipts/")