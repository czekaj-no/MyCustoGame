from django.shortcuts import render, redirect, get_object_or_404, redirect
from .models import Product, Order
from .cart import Cart
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Order, OrderItem
from django.contrib.admin.views.decorators import staff_member_required



def product_list(request):
    gry = Product.objects.filter(category='gra')
    quizy = Product.objects.filter(category='quiz')
    audiobooki = Product.objects.filter(category='audiobook')
    plyty = Product.objects.filter(category='plyta')

    context = {
        'gry': gry,
        'quizy': quizy,
        'audiobooki': audiobooki,
        'plyty': plyty,
    }
    return render(request, 'store/product_list.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    similar_products = Product.objects.exclude(id=product.id)[:3]
    return render(request, 'store/product_detail.html', {
        'product': product,
        'similar_products': similar_products
})

def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    cart = Cart(request)
    cart.add(product=product)
    return redirect('cart_detail')

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'store/cart_detail.html', {'cart': cart})

def remove_from_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    cart = Cart(request)
    cart.remove(product)
    return redirect('cart_detail')

@require_POST
def update_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    quantity = int(request.POST.get('quantity', 1))
    cart = Cart(request)
    cart.update(product, quantity)
    messages.success(request, f'Ilość produktu "{product.title}" została zaktualizowana.')
    return redirect('cart_detail')

def checkout(request):
    cart = Cart(request)

    if len(cart) == 0:
        messages.warning(request, "Twój koszyk jest pusty.")
        return redirect('product_list')

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        if not all([name, email, phone, address]):
            return render(request, 'store/checkout.html', {'cart': cart, 'error': 'Wszystkie pola są wymagane.'})

        order = Order.objects.create(
            name=name,
            email=email,
            phone=phone,
            address=address,
            is_paid=False
        )

        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['price']
            )

        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        from django.conf import settings

        # Email do klienta
        subject_client = 'Potwierdzenie zamówienia – MyCustoGame'
        message_client = render_to_string('emails/confirmation_email.html', {'order': order})
        send_mail(
            subject_client,
            '',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            html_message=message_client
        )

        # Email do admina
        subject_admin = 'Nowe zamówienie w sklepie MyCustoGame'
        message_admin = render_to_string('emails/admin_notification.html', {'order': order})
        send_mail(
            subject_admin,
            '',
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            html_message=message_admin
        )

        cart.clear()
        messages.success(request, "Dziękujemy za złożenie zamówienia!")
        return redirect('order_success')

    return render(request, 'store/checkout.html', {'cart': cart})

def order_success(request):
    return render(request, 'store/order_success.html')

def playable_products(request):
    gry = Product.objects.filter(category="gra", downloadable_file__isnull=False)
    quizy = Product.objects.filter(category="quiz", downloadable_file__isnull=False)
    audio = Product.objects.filter(category__in=["audiobook", "plyta"], downloadable_file__isnull=False)

    return render(request, 'store/playable_products.html', {
        'gry': gry,
        'quizy': quizy,
        'audio': audio,
    })