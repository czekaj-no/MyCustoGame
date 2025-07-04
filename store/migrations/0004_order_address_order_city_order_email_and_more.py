# Generated by Django 5.2 on 2025-05-12 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_remove_product_file_product_promo_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='address',
            field=models.CharField(default='adres', max_length=255),
        ),
        migrations.AddField(
            model_name='order',
            name='city',
            field=models.CharField(default='miasto', max_length=100),
        ),
        migrations.AddField(
            model_name='order',
            name='email',
            field=models.EmailField(default='email@example.com', max_length=254),
        ),
        migrations.AddField(
            model_name='order',
            name='first_name',
            field=models.CharField(default='imię', max_length=100),
        ),
        migrations.AddField(
            model_name='order',
            name='last_name',
            field=models.CharField(default='nazwisko', max_length=100),
        ),
        migrations.AddField(
            model_name='order',
            name='postal_code',
            field=models.CharField(default='00-000', max_length=20),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='price',
            field=models.DecimalField(decimal_places=2, default=500, max_digits=10),
        ),
    ]
