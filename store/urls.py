from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('zagraj/', views.playable_products, name='playable_products'),
    path('', views.product_list, name='product_list'),
    path('koszyk/', views.cart_detail, name='cart_detail'),
    path('zamowienie/', views.checkout, name='checkout'),
    path('zamowienie-sukces/', views.order_success, name='order_success'),
    path('aktualizuj-koszyk/<slug:slug>/', views.update_cart, name='update_cart'),
    path('zamowienie/', views.checkout, name='checkout'),
    path('konto/zamowienia/', views.my_orders_view, name='my_orders'),
    path('konto/dane/', views.my_data_view, name='my_data'),
    path('konto/personalizacja/', views.customization_view, name='customize'),
    path('konto/pliki/', views.downloads_view, name='downloads'),
    path('konto/kody/', views.qr_codes_view, name='qr_codes'),
    path('konto/oferty/', views.offers_view, name='offers'),
    path('konto/haslo/', auth_views.PasswordChangeView.as_view(template_name='store/password_change.html'), name='password_change'),
    path('konto/haslo/gotowe/', auth_views.PasswordChangeDoneView.as_view(template_name='store/password_change_done.html'), name='password_change_done'),
    path('<slug:slug>/', views.product_detail, name='product_detail'),
    path('dodaj-do-koszyka/<slug:slug>/', views.add_to_cart, name='add_to_cart'),
    path('usun-z-koszyka/<slug:slug>/', views.remove_from_cart, name='remove_from_cart'),

]


