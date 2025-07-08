from django.db import models
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        from .models import Profile  # import lokalny, żeby uniknąć konfliktu
        Profile.objects.create(user=instance)


class CustomForm(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class CustomFormField(models.Model):
    FIELD_TYPES = [
        ('text', 'Tekst'),
        ('textarea', 'Wielowierszowy tekst'),
        ('file', 'Plik (upload)'),
    ]
    form = models.ForeignKey(CustomForm, on_delete=models.CASCADE, related_name='fields')
    label = models.CharField(max_length=255)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)



class Product(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True, null=True)
    short_description = models.TextField(blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    promo_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='products/')
    tags = TaggableManager()
    downloadable_file = models.FileField(upload_to='downloads/', blank=True, null=True)
    custom_form = models.ForeignKey(
        CustomForm, on_delete=models.SET_NULL, null=True, blank=True,
        help_text="Formularz do personalizacji, który klient zobaczy w swoim panelu"
    )
    CATEGORY_CHOICES = [
        ('gra', 'Gra'),
        ('quiz', 'Quiz'),
        ('audiobook', 'Audiobook'),
        ('plyta', 'Płyta muzyczna'),
    ]

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='gra')


    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    images = models.ImageField(upload_to='products/gallery')

    def __str__(self):
        return f"{self.product.name} - image"

class Order(models.Model):
    STATUS_CHOICES = [
        ('nowe', 'Nowe'),
        ('w-trakcie','W trakcie realizacji'),
        ('zrealizowane', 'Zrealizowane'),
        ('anulowane', 'Anulowane'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='nowe')
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=150, blank=False, default="imię i nazwisko")
    email = models.EmailField(blank=False, default="email@example.com")
    phone = models.CharField(max_length=20, blank=False, default="123456789")
    address = models.CharField(max_length=255, blank=False, default="adres")
    postal_code = models.CharField(max_length=20, blank=False, default="00-000")
    city = models.CharField(max_length=100, blank=False, default="miasto")
    created = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Zamówienie #{self.id} - {self.name}"

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=500)
    quantity = models.PositiveIntegerField(default=1)
    ready_file = models.FileField(upload_to='user_files/', blank=True, null=True)


    def __str__(self):
        return f"{self.product.title} x{self.quantity}"

    def get_cost(self):
        return self.price * self.quantity


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    phone = models.CharField(max_length=20, blank=True)

    # Adres wysyłki
    shipping_street = models.CharField(max_length=255, blank=True)
    shipping_postcode = models.CharField(max_length=20, blank=True)
    shipping_city = models.CharField(max_length=100, blank=True)
    shipping_country = models.CharField(max_length=100, default="Polska", blank=True)

    # Faktura
    want_invoice = models.BooleanField(default=False)
    invoice_name = models.CharField(max_length=255, blank=True)
    invoice_nip = models.CharField(max_length=20, blank=True)
    same_as_shipping = models.BooleanField(default=True)

    invoice_street = models.CharField(max_length=255, blank=True)
    invoice_postcode = models.CharField(max_length=20, blank=True)
    invoice_city = models.CharField(max_length=100, blank=True)
    invoice_country = models.CharField(max_length=100, default="Polska", blank=True)

    def __str__(self):
        return f"Profil: {self.user.username}"


class QRCode(models.Model):
    order_item = models.ForeignKey('OrderItem', on_delete=models.CASCADE, related_name='qr_codes')
    url = models.URLField(verbose_name="Link docelowy", blank=True, null=True)  # teraz opcjonalny
    image = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    selected_for_card = models.BooleanField(default=False)

    is_active = models.BooleanField(default=False)
    was_edited = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created + timedelta(days=15)

    def __str__(self):
        return f"QR do {self.order_item.product.title} (ID {self.id})"


class Customization(models.Model):
    order_item = models.OneToOneField(OrderItem, on_delete=models.CASCADE, related_name='customization')
    form = models.ForeignKey(CustomForm, on_delete=models.CASCADE)
    sent = models.BooleanField(default=False)
    data = models.JSONField(blank=True, null=True)  # <-- TU zapisujemy dane z formularza


    def __str__(self):
        return f"Personalizacja: {self.order_item}"

class CustomizationFile(models.Model):
    customization = models.ForeignKey('Customization', on_delete=models.CASCADE, related_name='files')
    label = models.CharField(max_length=255)  # np. "Zdjęcie babci"
    file = models.FileField(upload_to='custom_files/')

    def __str__(self):
        return f"{self.label} ({self.customization})"


