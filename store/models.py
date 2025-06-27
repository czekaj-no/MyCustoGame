from django.db import models
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from django.utils.text import slugify



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
        ('zrealizowane', 'Zrealizowane'),
        ('anulowane', 'Anulowane'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=150, blank=False, default="imię i nazwisko")
    email = models.EmailField(blank=False, default="email@example.com")
    phone = models.CharField(max_length=20, blank=False, default="123456789")
    address = models.CharField(max_length=255, blank=False, default="adres")
    postal_code = models.CharField(max_length=20, blank=False, default="00-000")
    city = models.CharField(max_length=100, blank=False, default="miasto")
    created = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='nowe')


    def __str__(self):
        return f"Zamówienie #{self.id} - {self.name}"

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=500)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.title} x{self.quantity}"

    def get_cost(self):
        return self.price * self.quantity

