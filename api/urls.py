from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('api-token-auth/', obtain_auth_token),
    path('token/login/', views.custom_token_create_view, name='token_create'),
    path('users/me/', views.current_user, name='current_user'),
    path('users/', views.users, name='users'),
    path('menu-items/', views.MenuItemsView.as_view(), name='menu_items'),
    path('menu-items/<int:pk>/', views.SingleMenuItemView.as_view(), name='single-menu-item'),
]

