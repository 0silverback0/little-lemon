from rest_framework import serializers
from .models import Users, MenuItem

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['name','email','password']

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id','title','price','inventory']
        extra_kwargs = {
            'price': {'min_value': 2},
            'inventory':{'min_value':0}
        }
