"""
Конфигурация административного интерфейса ShopApp.

Содержит настройки отображения моделей,
кастомные действия и inline-конфигурации.
"""

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import path

from shopapp.models import Order, Product, ProductImage
from shopapp.admin_mixins import ExportAsCSVmixin
from .common import save_csv_products
from .forms import CSVImportForm


@admin.action(description="Archive products")
def mark_archived(modeladmin: admin.ModelAdmin,
                  request: HttpRequest,
                  queryset: QuerySet):
    """Admin action: archive selected products (soft delete)."""
    queryset.update(archived=True)


@admin.action(description="Unarchive products")
def mark_unarchived(modeladmin: admin.ModelAdmin,
                    request: HttpRequest,
                    queryset: QuerySet):
    """Admin action: unarchive selected products."""
    queryset.update(archived=False)


class ProductImageInline(admin.StackedInline):
    """Inline admin for ProductImage model."""

    model = ProductImage


class ProductInline(admin.TabularInline):
    """Inline admin for Order.products M2M relation."""

    model = Order.products.through


class OrderInline(admin.TabularInline):
    """Inline admin for Product.orders M2M relation."""

    model = Product.orders.through


# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin, ExportAsCSVmixin):
    """Admin configuration for Product model."""
    change_list_template = "shopapp/products-change-list.html"

    actions = [
        mark_archived,
        mark_unarchived,
        ExportAsCSVmixin.export_as_csv,
    ]
    inlines = [
            OrderInline,
            ProductImageInline,
    ]
    list_display = (
        "pk",
        "name",
        "description_short",
        "price",
        "discount",
        "archived"
    )
    list_display_links = "pk", "name"
    ordering = ("pk",)
    search_fields = "name", "description"
    fieldsets = [
        (None, {
            "fields": ("name", "description"),
        }),
        ("Price options", {
            "fields": ("price", "discount"),
            "classes": ("collapse",)
        }),
        ("Images", {
            "fields": ("preview",),
        }),
        ("Extra options", {
            "fields": ("archived",),
            "classes": ("collapse",),
            "description": "Extra options. "
                           "Field 'archived' is for soft delete."
        }),
    ]

    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == "GET":
            form = CSVImportForm()
            context = {
                "form": form,
            }
            return render(request, "admin/csv_form.html", context)
        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                "form": form,
            }
            return render(request, "admin/csv_form.html", context, status=400)
        # csv_file = TextIOWrapper(
        #     form.files["csv_file"].file,
        #     encoding=request.encoding,
        # )
        # reader = DictReader(csv_file)
        # products = [
        #     Product(**row)
        #     for row in reader
        # ]
        # Product.objects.bulk_create(products)
        save_csv_products(
                file=form.files["csv_file"].file,
                encoding=request.encoding,
            )
        self.message_user(request, "Data from CSV-files was imported")
        return redirect("..")

    def get_urls(self):
        urls = super().get_urls()
        new_urls=[
            path("import-products-csv/",
                 self.import_csv,
                 name="import_products_csv"
            ),
        ]
        return new_urls + urls

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin configuration for Order model."""

    inlines = [
        ProductInline,
    ]
    list_display = (
        "pk",
        "delivery_address",
        "promocode",
        "created_at",
        "user_verbose"
    )
    list_display_links = "pk", "delivery_address"
    ordering = ("-created_at",)

    def get_queryset(self, request):
        """Return optimized queryset for Order admin list view."""
        return (Order.objects.select_related("user").
                prefetch_related('products'))

    def user_verbose(self, obj: Order) -> str:
        """Return user display name for list_display column."""
        return ("%s %s" % (obj.user.first_name, obj.user.last_name)
                or obj.user.username).upper()


