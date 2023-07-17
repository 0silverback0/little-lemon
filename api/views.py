from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.decorators import permission_classes
from .serializers import UserSerializer, MenuItemSerializer
from .models import Users, MenuItem
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

# Create your views here.

# User registration and token generation endpoints

@api_view(['POST'])
def users(request):
    """ Create new user """
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

# Menu Items

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
        
class MenuItemsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.groups.filter(name="Manager").exists():
            menu_items = MenuItem.objects.all()
            serialized_items = MenuItemSerializer(menu_items, many=True)
            return Response({"menu items": serialized_items.data})
        elif request.user.groups.filter(name="Delivery crew"):
            menu_items = MenuItem.objects.all()
            serialized_items = MenuItemSerializer(menu_items, many=True)
            return Response({"menu items": serialized_items.data})
        else:
            return Response({"detail": "You are not authorized to access this resource."}, status=403)

    def post(self, request):
        if request.user.groups.filter(name="Manager").exists():
            serializer = MenuItemSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)
        else:
            return Response({"detail": "You are not authorized to access this resource."}, status=403)

    def delete(self, request):
        if request.user.groups.filter(name="Manager").exists():
            return Response({'res': 'deleted'})
        else:
            return Response({"detail": "You are not authorized to access this resource."}, status=403)