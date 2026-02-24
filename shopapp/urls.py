
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ShopIndexView,
    GropListView,
    ProductDetailsView,
    ProductsListView,
    OrderListView,
    OrderDetailView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    OrderCreateView,
    OrderUpdateView,
    OrderDeleteView,
    ProductsExportView,
    ProductViewSet,
)

app_name = "shopapp"

routers = DefaultRouter()
routers.register(r"products", ProductViewSet)

urlpatterns = [
    path("", ShopIndexView.as_view() , name="index"),
    path("api/", include(routers.urls)),
    path("groups/", GropListView.as_view(), name="groups_list"),
    path("products/", ProductsListView.as_view(), name="products_list"),
    path("products/create/", ProductCreateView.as_view(), name="product_create"),
    path("products/<int:pk>/", ProductDetailsView.as_view(), name ="product_details"),
    path("products/confirm-delete/<int:pk>/", ProductDeleteView.as_view(), name ="product_delete"),
    path("products/update/<int:pk>/", ProductUpdateView.as_view(), name ="product_update"),
    path("products/export", ProductsExportView.as_view(), name ="products-export"),
    path("orders/", OrderListView.as_view(), name="orders_list"),
    path("orders/create/", OrderCreateView.as_view(), name="order_create"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order_details"),
    path("orders/confirm-delete/<int:pk>/", OrderDeleteView.as_view(), name="order_delete"),
    path("orders/update/<int:pk>/", OrderUpdateView.as_view(), name="order_update"),
]
