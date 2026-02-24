import logging
from csv import DictWriter
from timeit import default_timer

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from drf_spectacular.utils import extend_schema, OpenApiResponse
from yaml import serialize

from .models import Product, Order, ProductImage
from .forms import GroupForm, ProductForm
from .serialiizers import ProductSerializer
from .common import save_csv_products

log = logging.getLogger(__name__)

@extend_schema(description="Products views CRUD")
class ProductViewSet(ModelViewSet):
    """
    ViewSet для работы с товарами (Product).

    Предоставляет полный набор REST-операций для модели Product:
    - получение списка товаров;
    - получение одного товара по идентификатору;
    - создание нового товара;
    - обновление и частичное обновление товара;
    - удаление товара.

    Поддерживаемые возможности:
    - поиск по названию и описанию товара;
    - фильтрация по основным полям модели;
    - сортировка результатов запроса.

    Используемые фильтры:
    - SearchFilter — для текстового поиска;
    - DjangoFilterBackend — для точной фильтрации;
    - OrderingFilter — для сортировки.

    По умолчанию результаты сортируются по первичному ключу (pk).
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]

    search_fields = [
        "name",
        "description",
    ]

    filterset_fields = [
        "name",
        "description",
        "price",
        "discount",
        "archived",
    ]

    ordering_fields = ["pk"]
    ordering = ["pk"]

    @extend_schema(
        summary="Get one product dy ID",
        description="Retrievers **product**, returns 404 if not found",
        responses={
            200: ProductSerializer,
            404: OpenApiResponse(description="Empty response, product by ID not found"),
        }
    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)

    @action(methods=["get"], detail=False)
    def download_csv(self, request: Request):
        response = HttpResponse(content_type='text/csv')
        filename = 'products-export.csv'
        response['Content-Disposition'] = f'attachment; filename={filename}'
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            "name",
            "description",
            "price",
            "discount",
        ]
        queryset = queryset.only(*fields)
        write = DictWriter(response, fieldnames=fields)
        write.writeheader()

        for product in queryset:
            write.writerow({
                field: getattr(product, field)
                for field in fields
            })
        return response

    @action(
        methods=["post"],
        detail=False,
        parser_classes=[MultiPartParser],
    )
    def upload_csv(self, request: Request):
        products = save_csv_products(
            file=request.FILES['file'].file,
            encoding=request.encoding,
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class ShopIndexView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            ("laptop", 1999),
            ("desktop", 2999),
            ("mobile", 999),
        ]
        context = {
            "time_running": default_timer(),
            "products": products,
        }
        log.debug("Products for shop index: %s",products)
        log.info("Rendering shop index")
        print("shop index context", context)
        return render(
            request,
            "shopapp/shop-index.html",
            context=context,
        )


class GropListView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            "form": GroupForm(),
            "groups": Group.objects.prefetch_related('permissions').all()
        }
        return render(
            request,
            "shopapp/groups-list.html",
            context=context,
        )
    def post(self, request: HttpRequest) -> HttpResponse:
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect(request.path)


class ProductDetailsView(DetailView):
    template_name = "shopapp/products-details.html"
    model = Product
    context_object_name = "product"


class ProductsListView(ListView):
    # model = Product
    queryset = Product.objects.select_related("images")
    template_name = "shopapp/products-list.html"
    context_object_name = "products"

    def get_queryset(self):
        return Product.objects.filter(archived=False)


class ProductCreateView(CreateView):
    model = Product
    fields = "__all__"
    success_url = reverse_lazy("shopapp:products_list")


class ProductUpdateView(UpdateView):
    model = Product
    template_name_suffix = "_update_form"
    form_class = ProductForm

    def get_success_url(self):
        return reverse(
            "shopapp:product_details",
                      kwargs={"pk": self.object.pk},
        )

    def form_valid(self, form):
        response = super().form_valid(form)

        images = self.request.FILES.getlist("images")

        # Если новые изображения вообще пришли
        if images:
            # 1. удаляем старые изображения (и файлы, и записи)
            self.object.images.all().delete()

            # 2. сохраняем только новые
            for image in images:
                ProductImage.objects.create(
                    product=self.object,
                    image=image,
                )
        return response


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy("shopapp:products_list")

    def  form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class OrderListView(LoginRequiredMixin, ListView):
    queryset = (Order.objects
        .select_related("user")
        .prefetch_related("products")
    )


class OrderDetailView(DetailView):
    queryset = (
        Order.objects.select_related("user").prefetch_related("products")
    )


class OrderCreateView(CreateView):
    model = Order
    fields = "__all__"
    success_url = reverse_lazy("shopapp:orders_list")


class OrderUpdateView(UpdateView):
    model = Order
    fields = "__all__"
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse(
            "shopapp:order_details",
            kwargs={"pk": self.object.pk},
        )

class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy("shopapp:orders_list")

    def  form_valid(self, form):
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)


class ProductsExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        cache_key = "products_data_export"
        products_data = cache.get(cache_key)
        if products_data is None:
            products = Product.objects.order_by("pk").all()
            products_data = [
                {
                    "pk": product.pk,
                    "name": product.name,
                    "price": product.price,
                    "archived": product.archived,
                }
            for product in products
            ]
        cache.set(cache_key, products_data, 300)
        return JsonResponse({"products": products_data})
