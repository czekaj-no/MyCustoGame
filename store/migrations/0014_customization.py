# Generated by Django 5.2 on 2025-07-02 21:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0013_alter_order_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sent', models.BooleanField(default=False)),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.customform')),
                ('order_item', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='customization', to='store.orderitem')),
            ],
        ),
    ]
