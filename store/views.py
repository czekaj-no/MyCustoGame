from django.shortcuts import render, redirect, get_object_or_404, redirect
from .models import Product, Order
from .cart import Cart
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Order, OrderItem, Profile, QRCode
from .forms import QRCodeForm
from django.utils import timezone
from datetime import timedelta, date
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile


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

@login_required
def my_orders_view(request):
    # Na razie pusta lista testowa – zamówienia dodamy później z modeli
    return render(request, 'store/my_orders.html')



@login_required
def my_data_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    # ALERT: czy użytkownik ma zamówienia fizyczne bez adresu?
    show_address_alert = False  # <- uzupełnimy później

    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()

        profile.phone = request.POST.get('phone', '')

        profile.shipping_street = request.POST.get('shipping_street', '')
        profile.shipping_postcode = request.POST.get('shipping_postcode', '')
        profile.shipping_city = request.POST.get('shipping_city', '')
        profile.shipping_country = request.POST.get('shipping_country', '')

        profile.want_invoice = 'want_invoice' in request.POST
        profile.invoice_name = request.POST.get('invoice_name', '')
        profile.invoice_nip = request.POST.get('invoice_nip', '')
        profile.same_as_shipping = 'same_as_shipping' in request.POST

        if not profile.same_as_shipping:
            profile.invoice_street = request.POST.get('invoice_street', '')
            profile.invoice_postcode = request.POST.get('invoice_postcode', '')
            profile.invoice_city = request.POST.get('invoice_city', '')
            profile.invoice_country = request.POST.get('invoice_country', '')

        profile.save()
        messages.success(request, "Dane zostały zapisane!")
        return redirect('my_data')

    return render(request, 'store/my_data.html', {
        'profile': profile,
        'show_address_alert': show_address_alert,
    })





@login_required
def customization_view(request):
    # Lista formularzy przypisanych do zamówień użytkownika
    customizations = []

    for order in Order.objects.filter(user=request.user, status="waiting"):
        form_obj = Customization.objects.get_or_create(order=order)[0]
        # Tutaj podkładasz konkretny formularz, np. zdefiniowany osobno dla każdego produktu
        form = get_custom_form_for_product(order.product, instance=form_obj)
        customizations.append({
            "product": order.product,
            "form": form,
            "id": form_obj.id,
            "sent": form_obj.sent
        })

    if request.method == "POST":
        for item in customizations:
            form_id = item["id"]
            if f"send-{form_id}" in request.POST or f"save-{form_id}" in request.POST:
                form = get_custom_form_for_product(item["product"], request.POST, instance=form_obj)
                if form.is_valid():
                    form.save()
                    if f"send-{form_id}" in request.POST:
                        form_obj.sent = True
                        form_obj.save()
                return redirect("customize")  # reload po zapisie

    return render(request, "store/customization_form.html", {
        "customizations": customizations
    })

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def downloads_view(request):
    user_orders = request.user.order_set.all()
    ready_items = []

    for order in user_orders:
        for item in order.items.all():
            if item.ready_file:
                ready_items.append(item)

    return render(request, 'store/downloads.html', {
        'ready_items': ready_items
    })


@login_required
def qr_codes_view(request):
    order_items = OrderItem.objects.filter(order__user=request.user)
    context = {'items': []}

    # Obsługa formularza
    if request.method == 'POST':
        form = QRCodeForm(request.POST)
        item_id = request.POST.get('item_id')

        if form.is_valid() and item_id:
            item = OrderItem.objects.get(id=item_id, order__user=request.user)

            wants_card = 'selected_for_card' in request.POST
            user_has_card = OrderItem.objects.filter(
                order__user=request.user,
                product__title__icontains='kartka'
            ).exists()

            if wants_card and not user_has_card:
                messages.error(request, "Aby wybrać kod QR do kartki, najpierw ją zakup.")
                return redirect('qr_codes')

            if item.qr_codes.count() >= 3:
                messages.error(request, "Możesz wygenerować maksymalnie 3 kody QR dla jednego produktu.")
                return redirect('qr_codes')

            qr = form.save(commit=False)
            qr.order_item = item
            qr.image = generate_qr_image(qr.url)
            qr.save()
            messages.success(request, "Kod QR został wygenerowany!")
            return redirect('qr_codes')

    # GET – pokaż formularze
    for item in order_items:
        qrs = item.qr_codes.all()
        context['items'].append({
            'item': item,
            'qrs': qrs,
            'remaining_slots': 3 - qrs.count()
        })

    return render(request, 'store/qr_generator.html', context)



@login_required
def offers_view(request):
    return render(request, 'store/offers.html')

    @login_required
    def offers_view(request):
        today = date.today()

     # Czy użytkownik ma chociaż jedno zrealizowane zamówienie?
        has_realized_order = Order.objects.filter(user=request.user, status='zrealizowane').exists()

        # Limit czasowy dla oferty z pendrivem
        pendrive_deadline = today + timedelta(days=7)

        show_pendrive_offer = today <= pendrive_deadline  # tylko jeśli jeszcze ważna

        context = {
            'has_realized_order': has_realized_order,
            'show_pendrive_offer': show_pendrive_offer,
            'pendrive_deadline': pendrive_deadline,
        }
        return render(request, 'store/offers.html', context)

def generate_qr_image(url):
    qr = qrcode.make(url)
    buffer = BytesIO()
    qr.save(buffer)
    filename = "qr.png"
    return ContentFile(buffer.getvalue(), name=filename)