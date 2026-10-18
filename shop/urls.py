from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('track/<int:order_id>/', views.order_track, name='order_track'),
    path('order/<int:order_id>/invoice/', views.order_invoice, name='order_invoice'),

    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_favorite, name='toggle_favorite'),

    path('gift-card/', views.buy_gift_card, name='buy_gift_card'),
    path('gift-card/use/', views.use_gift_card, name='use_gift_card'),


    path('seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('seller/add-product/', views.seller_add_product, name='seller_add_product'),
    path('seller/order/<int:order_id>/status/', views.seller_update_status, name='seller_update_status'),
    path('seller/export-csv/', views.seller_export_csv, name='seller_export_csv'),

    path('register/', views.register, name='register'),
]
