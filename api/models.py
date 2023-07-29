from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Users(models.Model):
    name = models.CharField(max_length=255)
    email =models.EmailField()
    password = models.CharField(max_length=16)

class MenuItem(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    inventory = models.SmallIntegerField()

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

class OrderItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    delivery_crew = models.ForeignKey(User, related_name='order_delivery_crew', on_delete=models.SET_NULL, blank=True, null=True)
    status = models.IntegerField(choices=[(0, 'Out for Delivery'), (1, 'Delivered')], blank=True, null=True)