from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("menu/", views.product_list, name="product_list"),
    path("cart/", views.cart, name="cart"),
    path("checkout/", views.checkout, name="checkout"),

    path("place-order/", views.place_order, name="place_order"),  # ⭐ ADD THIS

    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("register/", views.user_register, name="register"),

    path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("remove-from-cart/<int:product_id>/", views.remove_from_cart, name="remove_from_cart"),

    path("product/<int:product_id>/", views.product_detail, name="product_detail"),
    
    # Delivery System URLs
    path("delivery-addresses/", views.delivery_addresses, name="delivery_addresses"),
    path("add-delivery-address/", views.add_delivery_address, name="add_delivery_address"),
    path("edit-delivery-address/<int:address_id>/", views.edit_delivery_address, name="edit_delivery_address"),
    path("delete-delivery-address/<int:address_id>/", views.delete_delivery_address, name="delete_delivery_address"),
    
    # Order & Tracking URLs
    path("order/<int:order_id>/", views.order_detail, name="order_detail"),
    path("order-history/", views.order_history, name="order_history"),
    path("track-order/<int:order_id>/", views.track_order, name="track_order"),
    path("api/delivery-status/<int:order_id>/", views.delivery_status_api, name="delivery_status_api"),
]

