# Generated by Django 4.2.3 on 2023-07-26 12:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0005_orderitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='delivery_crew',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='order_delivery_crew', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='status',
            field=models.IntegerField(blank=True, choices=[(0, 'Out for Delivery'), (1, 'Delivered')], null=True),
        ),
    ]
