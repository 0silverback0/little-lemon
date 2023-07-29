from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Users, MenuItem, CartItem, Cart, OrderItem

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

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = '__all__'  # Include all fields or specify the fields you want to include

class CartItemSerializer(serializers.ModelSerializer):
    menu_item = MenuItemSerializer()

    class Meta:
        model = CartItem
        fields = '__all__'

class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'user', 'menu_item', 'quantity', 'created_at', 'delivery_crew', 'status']
        # read_only_fields = ['id', 'user', 'created_at', 'delivery_crew', 'status']

