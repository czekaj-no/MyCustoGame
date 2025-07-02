from django.contrib import admin
from .models import Product, Order, OrderItem, CustomForm, CustomFormField, Customization


# Rejestracja prostych modeli
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'price']  # możesz dodać więcej, jeśli chcesz
    fields = ['title', 'category', 'price', 'downloadable_file', 'custom_form']


admin.site.register(OrderItem)  # OrderItem sam w sobie

# Konfiguracja Order z dekoratorem
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ['product', 'quantity', 'ready_file', 'get_customer']
    readonly_fields = ['get_customer']

    def get_customer(self, obj):
        return f"{obj.order.name} ({obj.order.email})"

    get_customer.short_description = "Klient"

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'is_paid', 'created', 'status']
    list_filter = ['is_paid', 'status']
    search_fields = ['name', 'email']
    inlines = [OrderItemInline]
    list_editable = ['status', 'is_paid']

class CustomFormFieldInline(admin.TabularInline):
    model = CustomFormField
    extra = 1

@admin.register(CustomForm)
class CustomFormAdmin(admin.ModelAdmin):
    inlines = [CustomFormFieldInline]

@admin.register(Customization)
class CustomizationAdmin(admin.ModelAdmin):
    list_display = ['order_item', 'form', 'sent']
    readonly_fields = ['form', 'order_item']



