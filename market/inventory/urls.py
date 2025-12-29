from django.urls import path
from inventory import views as inventory_views


app_name = "inventory"

urlpatterns = [
    path('', inventory_views.products_view, name='products'),
    path('<int:pk>/', inventory_views.product_detail_view, name='product_detail'),
    path('add/', inventory_views.add_product_view, name='add_product'),
    path('<int:pk>/edit/', inventory_views.edit_product_view, name='edit_product'),
    path('<int:pk>/delete/', inventory_views.delete_product_view, name='delete_product'),
    path('cart/', inventory_views.cart_view, name='cart'),
    path('<int:pk>/add-to-cart/', inventory_views.add_to_cart_view, name='add_to_cart'),
    path('cart/<int:pk>/remove/', inventory_views.remove_from_cart_view, name='remove_from_cart'),
    path('cart/<int:pk>/update/', inventory_views.update_cart_quantity_view, name='update_cart_quantity'),
    path('cart/purchase/', inventory_views.purchase_view, name='purchase'),
]