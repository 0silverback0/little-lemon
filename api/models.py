from django.db import models

# Create your models here.

class Users(models.Model):
    name = models.CharField(max_length=255)
    email =models.EmailField()
    password = models.CharField(max_length=16)

class MenuItem(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    inventory = models.SmallIntegerField()
