from django.urls import path
from inventory import views as inventory_views


app_name = "inventory"

urlpatterns = [
    path('', inventory_views.products_view, name='products'),
    path('add/', inventory_views.add_product_view, name='add_product'),
    path('<int:pk>/edit/', inventory_views.edit_product_view, name='edit_product'),
    path('<int:pk>/delete/', inventory_views.delete_product_view, name='delete_product'),
]