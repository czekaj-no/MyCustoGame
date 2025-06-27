from django.urls import path
from . import views

urlpatterns = [
    path('zagraj/', views.playable_products, name='playable_products'),
    path('', views.product_list, name='product_list'),
    path('koszyk/', views.cart_detail, name='cart_detail'),
    path('zamowienie/', views.checkout, name='checkout'),
    path('zamowienie-sukces/', views.order_success, name='order_success'),
    path('<slug:slug>/', views.product_detail, name='product_detail'),
    path('dodaj-do-koszyka/<slug:slug>/', views.add_to_cart, name='add_to_cart'),
    path('usun-z-koszyka/<slug:slug>/', views.remove_from_cart, name='remove_from_cart'),
    path('aktualizuj-koszyk/<slug:slug>/', views.update_cart, name='update_cart'),
    path('zamowienie/', views.checkout, name='checkout'),
]


