from django.contrib import admin
from .models import Product, Order, OrderItem

# Rejestracja prostych modeli
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'price']  # możesz dodać więcej, jeśli chcesz

admin.site.register(OrderItem)  # OrderItem sam w sobie

# Konfiguracja Order z dekoratorem
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'is_paid', 'created', 'status']
    list_filter = ['is_paid', 'status']
    search_fields = ['name', 'email']
    inlines = [OrderItemInline]
    list_editable = ['status', 'is_paid']

