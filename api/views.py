from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status as http_status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from .serializers import UserSerializer, MenuItemSerializer, CustomUserSerializer, CartItemSerializer, OrderItemSerializer
from .models import Users, MenuItem, Cart, CartItem, OrderItem
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Group, User
from django.contrib.auth import get_user_model
from django.db import models
from rest_framework.generics import RetrieveAPIView, CreateAPIView, DestroyAPIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


# Create your views here.

# User registration and token generation endpoints

@api_view(['POST'])
def users(request):
    """ Create new user """
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(serializer.data, status=http_status.HTTP_201_CREATED)
    return Response(serializer.errors, status=http_status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """ Get current user """
    user = request.user
    
    data = {
        'username': user.username,
        'email': user.email,
        
    }
    return Response(data)

class CustomTokenCreateView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        """ create token """
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})

custom_token_create_view = CustomTokenCreateView.as_view()

#### Menu Items #####

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated]


    def get(self, request, *args, **kwargs):
        user = request.user
        if request.method == 'GET':
            # Retrieve the menu item based on the provided primary key
            return self.retrieve(request, *args, **kwargs)
        else:
            return Response({"detail": "You are not authorized to access this resource."}, status=403)
        
    def post(self, request, pk):
        if request.method == 'POST':
            return Response({"detail": "You are not authorized to access this resource."}, status=403)
        
    def put(self, request, pk):
        if request.user.groups.filter(name="Delivery crew"):
            return Response({"detail": "You are not authorized to access this resource."}, status=403)
        else:
            menu_item = get_object_or_404(MenuItem, pk=pk)
            serializer = MenuItemSerializer(menu_item, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
        return Response(serializer.errors, status=400)

        
    def patch(self, request, pk):
        if request.user.groups.filter(name="Delivery crew"):
            return Response({"detail": "You are not authorized to access this resource."}, status=403)
        else:
            menu_item = get_object_or_404(MenuItem, pk=pk)
            serializer = MenuItemSerializer(menu_item, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
        return Response(serializer.errors, status=400)

        
    def delete(self, request, pk):
        if request.user.groups.filter(name="Delivery crew").exists():
            return Response({"detail": "You are not authorized to access this resource."}, status=403)
        else:
            menu_item = get_object_or_404(MenuItem, pk=pk)
            menu_item.delete()
            return Response({"detail": "Menu item deleted."}, status=204)
        
class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class MenuItemsView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MenuItemSerializer
    queryset = MenuItem.objects.all()
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'price']
    ordering_fields = ['title', 'price']
    pagination_class = CustomPageNumberPagination
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get_queryset(self):
        # Apply filtering based on 'title' and 'price' query parameters
        title = self.request.query_params.get('title', None)
        price = self.request.query_params.get('price', None)
        queryset = MenuItem.objects.all()

        if title:
            queryset = queryset.filter(title__icontains=title)

        if price:
            queryset = queryset.filter(price=price)

        return queryset

    def post(self, request):
        if not request.user.groups.filter(name="Manager").exists():
            return Response({"detail": "You are not authorized to access this resource."}, status=403)

        serializer = MenuItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def patch(self, request):
        if request.method == 'PATCH' and request.user.groups.filter(name="Delivery crew").exists():
            return Response({'patch': 'not allowed'}, status=403)
        else:
            return Response({'user': 'allowed'})

    def delete(self, request):
        if not request.user.groups.filter(name="Manager").exists():
            return Response({"detail": "You are not authorized to access this resource."}, status=403)

        return Response({'res': 'deleted'})
    
    ### User group management ###

class ManagersListView(RetrieveAPIView, CreateAPIView, DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = get_user_model().objects.all()

    def get(self, request, *args, **kwargs):
        if 'pk' in kwargs:  # Check if 'pk' (userId) is provided in the URL
            return self.retrieve(request, *args, **kwargs)  # Use RetrieveAPIView for GET requests with 'pk'
        try:
            if request.user.groups.filter(name="Manager").exists():
                manager_group = Group.objects.get(name='Manager')
                managers = get_user_model().objects.filter(groups=manager_group)
                serializer = CustomUserSerializer(managers, many=True)
                return Response(serializer.data)
            else:
                return Response({"detail": "You are not authorized to access this resource."}, status=http_status.HTTP_403_FORBIDDEN)
        except Group.DoesNotExist:
            return Response({"detail": "Manager group not found."}, status=http_status.HTTP_404_NOT_FOUND)

    def post(self, request, *args, **kwargs):
        #Make this DRY for all views
        if request.user.groups.filter(name="Manager").exists():
            # Access user data from the request body
            username = request.data.get('username')
            email = request.data.get('email')
            password = request.data.get('password')

            # Get the User model (default or custom)
            User = get_user_model()

            # Create a new user instance
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            # Assign the user to the "Manager" group
            manager_group = Group.objects.get(name="Manager")
            user.groups.add(manager_group)

            return Response({"detail": "User created and assigned to Manager group."}, status=http_status.HTTP_201_CREATED)
        else:
            return Response({"detail": "You are not authorized to create users or assign them to the Manager group."}, status=http_status.HTTP_403_FORBIDDEN)

    def delete(self, request, *args, **kwargs):
        if 'pk' in kwargs:  # Check if 'pk' (userId) is provided in the URL
            if request.user.groups.filter(name="Manager").exists():
                user_id = kwargs.get('pk')
                try:
                    user = get_user_model().objects.get(pk=user_id)
                except get_user_model().DoesNotExist:
                    return Response({"detail": "User not found."}, status=http_status.HTTP_404_NOT_FOUND)

                # Remove the user from the "Manager" group
                manager_group = Group.objects.get(name="Manager")
                user.groups.remove(manager_group)

                return Response({"detail": "User removed from Manager group."}, status=http_status.HTTP_200_OK)
            else:
                return Response({"detail": "You are not authorized to remove users from the Manager group."}, status=http_status.HTTP_403_FORBIDDEN)
        else:
            return Response({"detail": "You must provide a valid userId in the URL for DELETE requests."}, status=http_status.HTTP_400_BAD_REQUEST)
        
class DeliveryCrewListView(RetrieveAPIView, CreateAPIView, DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomUserSerializer

    def get(self, request):
        try:
            if request.user.groups.filter(name="Manager").exists():
                delivery_crew_group = Group.objects.get(name='Delivery crew')
                delivery_crew_members = get_user_model().objects.filter(groups=delivery_crew_group)
                serializer = CustomUserSerializer(delivery_crew_members, many=True)
                return Response(serializer.data)
            else:
                return Response({"detail": "You are not authorized to access this resource."}, status=http_status.HTTP_403_FORBIDDEN)
        except Group.DoesNotExist:
            return Response({"detail": "Manager group not found."}, status=http_status.HTTP_404_NOT_FOUND)
        
    def post(self, request):
        if request.user.groups.filter(name="Manager").exists():
            # Access user data from the request body
            username = request.data.get('username')
            email = request.data.get('email')
            password = request.data.get('password')

            # Get the User model (default or custom)
            User = get_user_model()

            # Create a new user instance
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            # Assign the user to the "Manager" group
            delivery_crew_group = Group.objects.get(name="Delivery crew")
            user.groups.add(delivery_crew_group)

            return Response({"detail": "User created and assigned to Manager group."}, status=http_status.HTTP_201_CREATED)
        else:
            return Response({"detail": "You are not authorized to create users or assign them to the Manager group."}, status=http_status.HTTP_403_FORBIDDEN)

    def delete(self, request, *args, **kwargs):
        if 'pk' in kwargs:  # Check if 'pk' (userId) is provided in the URL
            if request.user.groups.filter(name="Manager").exists():
                user_id = kwargs.get('pk')
                try:
                    user = get_user_model().objects.get(pk=user_id)
                except get_user_model().DoesNotExist:
                    return Response({"detail": "User not found."}, status=http_status.HTTP_404_NOT_FOUND)

                # Remove the user from the "Manager" group
                delivery_crew_group= Group.objects.get(name="Delivery crew")
                user.groups.remove(delivery_crew_group)

                return Response({"detail": "User removed from Manager group."}, status=http_status.HTTP_200_OK)
            else:
                return Response({"detail": "You are not authorized to remove users from the Manager group."}, status=http_status.HTTP_403_FORBIDDEN)
        else:
            return Response({"detail": "You must provide a valid userId in the URL for DELETE requests."}, status=http_status.HTTP_400_BAD_REQUEST)
        
class CartItemsListView(RetrieveAPIView, CreateAPIView, DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the current user based on the provided token
        user = request.user

        try:
            # Fetch the user's cart
            cart = Cart.objects.get(user=user)

            # Fetch all cart items associated with the cart
            cart_items = CartItem.objects.filter(cart=cart)

            # Serialize the cart items
            serializer = CartItemSerializer(cart_items, many=True)
            return Response(serializer.data)
        except Cart.DoesNotExist:
            return Response({"detail": "Cart not found for the current user."}, status=http_status.HTTP_404_NOT_FOUND)


    def post(self, request):
        # Get the current user's cart or create a new one if it doesn't exist
        cart, created = Cart.objects.get_or_create(user=request.user)

        # Get the menu item data from the request data
        menu_item_id = request.data.get('menu_item_id')
        quantity = request.data.get('quantity')

        try:
            menu_item = MenuItem.objects.get(pk=menu_item_id)
        except MenuItem.DoesNotExist:
            return Response({"detail": "Menu item not found."}, status=http_status.HTTP_404_NOT_FOUND)

        # Create or update the cart item
        cart_item, created = CartItem.objects.get_or_create(cart=cart, menu_item=menu_item)
        cart_item.quantity = quantity
        cart_item.save()

        # Serialize the cart item and return the response
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=http_status.HTTP_201_CREATED)
    
    def delete(self, request):
        # Get the current user's cart if it exists
        try:
            cart = Cart.objects.get(user=request.user)

            # Delete all cart items associated with the cart
            CartItem.objects.filter(cart=cart).delete()
            return Response({"detail": "All menu items in the cart have been deleted."}, status=http_status.HTTP_200_OK)
        
        except Cart.DoesNotExist:
            return Response({"detail": "Cart not found for the current user."}, status=http_status.HTTP_404_NOT_FOUND)

class OrderCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.groups.filter(name="Manager").exists():
            # If user is a manager, return all order items
            order_items = OrderItem.objects.all()
        elif request.user.groups.filter(name="Delivery crew").exists():
            # If user is a delivery crew, return orders assigned to them
            order_items = OrderItem.objects.filter(delivery_crew=request.user)
            print("Delivery crew user ID:", request.user.id)
            print("Order items for delivery crew:", order_items)
        else:
            # If user is a customer, return their order items only
            user = request.user
            order_items = OrderItem.objects.filter(user=user)

        serializer = OrderItemSerializer(order_items, many=True)
        return Response(serializer.data)

    def post(self, request):

        if request.user.groups.filter(name="Customer").exists():
            user = request.user

            # Get current cart items for the user
            cart_items = CartItem.objects.filter(cart__user=user)

            # Create order items from cart items
            order_items = []
            for cart_item in cart_items:
                order_item = OrderItem(
                    user=user,
                    menu_item=cart_item.menu_item,
                    quantity=cart_item.quantity
                )
                order_items.append(order_item)

            # Save order items to the database
            OrderItem.objects.bulk_create(order_items)

            # Delete cart items for the user
            cart_items.delete()

            return Response({"detail": "Order created successfully."}, status=http_status.HTTP_201_CREATED)
        
        else:
            return Response({"detail": "You are not authorized "}, status=http_status.HTTP_403_FORBIDDEN)
        
class OrderItemsView(APIView):
    permission_classes = [IsAuthenticated]

    def check_manager_permission(self, request):
        return request.user.groups.filter(name="Manager").exists()

    def check_customer_permission(self, request):
        return request.user.groups.filter(name="Customer").exists()

    def check_delivery_crew_permission(self, request):
        return request.user.groups.filter(name="Delivery crew").exists()


    def get_order_item(self, orderId):
        try:
            order_item = OrderItem.objects.get(id=orderId)
            return order_item
        except OrderItem.DoesNotExist:
            return None

    def get(self, request, orderId):
        order_item = self.get_order_item(orderId)
        if not order_item:
            return Response({"detail": "Order not found."}, status=http_status.HTTP_404_NOT_FOUND)

        # Check if the order belongs to the current user
        if order_item.user != request.user:
            return Response({"detail": "This order does not belong to the current user."}, status=http_status.HTTP_403_FORBIDDEN)

        serializer = OrderItemSerializer(order_item)
        return Response(serializer.data)

    def put(self, request, orderId):
        order_item = self.get_order_item(orderId)
        if not order_item:
            return Response({"detail": "Order not found."}, status=http_status.HTTP_404_NOT_FOUND)

        # Check if the current user is a manager
        if not self.check_manager_permission(request):
            return Response({"detail": "You are not authorized to perform this action."}, status=http_status.HTTP_403_FORBIDDEN)

        delivery_crew_id = request.data.get('delivery_crew')
        status = request.data.get('status')

        if delivery_crew_id is not None:
            try:
                delivery_crew = User.objects.get(pk=delivery_crew_id)
                order_item.delivery_crew = delivery_crew
            except User.DoesNotExist:
                return Response({"detail": "Invalid delivery crew ID."}, status=http_status.HTTP_400_BAD_REQUEST)

        if status is not None:
            order_item.status = status

        order_item.save()
        serializer = OrderItemSerializer(order_item)
        return Response(serializer.data, status=http_status.HTTP_200_OK)


    def patch(self, request, orderId):
        order_item = self.get_order_item(orderId)
        if not order_item:
            return Response({"detail": "Order not found."}, status=http_status.HTTP_404_NOT_FOUND)

        # Check if the current user is a manager
        if self.check_manager_permission(request):
            # Managers can't use the PATCH method for updating, so return 405 Method Not Allowed
            return Response({"detail": "Method not allowed for managers."}, status=http_status.HTTP_405_METHOD_NOT_ALLOWED)

        # For customers and delivery crew, allow updating 'quantity' and 'menu_item' fields
        if self.check_customer_permission(request):# or request.user.groups.filter(name="Delivery crew").exists():
            serializer = OrderItemSerializer(order_item, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=http_status.HTTP_200_OK)
            return Response(serializer.errors, status=http_status.HTTP_400_BAD_REQUEST)
        
         # For delivery crew, allow updating 'status' field
        if self.check_delivery_crew_permission(request):
            serializer = OrderItemSerializer(order_item, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=http_status.HTTP_200_OK)
            return Response(serializer.errors, status=http_status.HTTP_400_BAD_REQUEST)

        # Return 403 Forbidden for other user types
        return Response({"detail": "You are not authorized to perform this action."}, status=http_status.HTTP_403_FORBIDDEN)

    def delete(self, request, orderId):
        order_item = self.get_order_item(orderId)
        if not order_item:
            return Response({"detail": "Order not found."}, status=http_status.HTTP_404_NOT_FOUND)

        # Check if the current user is a manager
        if not self.check_manager_permission(request):
            return Response({"detail": "You are not authorized to perform this action."}, status=http_status.HTTP_403_FORBIDDEN)

        # Delete the order item
        order_item.delete()
        return Response({"detail": "Order deleted successfully."}, status=http_status.HTTP_200_OK)