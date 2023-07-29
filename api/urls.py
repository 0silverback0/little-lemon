from django.urls import path
from . import views
from .views import SingleMenuItemView, MenuItemsView, ManagersListView, DeliveryCrewListView, CartItemsListView, OrderCreateView, OrderItemsView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('api-token-auth/', obtain_auth_token),
    path('token/login/', views.custom_token_create_view, name='token_create'),
    path('users/me/', views.current_user, name='current_user'),
    path('users/', views.users, name='users'),
    path('menu-items/', MenuItemsView.as_view(), name='menu_items'),
    path('menu-items/<int:pk>/', SingleMenuItemView.as_view(), name='single-menu-item'),
    path('groups/manager/users/', ManagersListView.as_view(), name='managers-list'),
    path('groups/manager/users/<int:pk>', ManagersListView.as_view(), name='managers-list'),
    path('groups/delivery-crew/users/', DeliveryCrewListView.as_view(), name='delivery-crew-list'),
    path('groups/delivery-crew/users/<int:pk>', DeliveryCrewListView.as_view(), name='delivery-crew-list'),
    path('cart/menu-items/', CartItemsListView.as_view(), name='cart-items'),
    path('orders/', OrderCreateView.as_view(), name='order-create'),
    path('orders/<int:orderId>/', OrderItemsView.as_view(), name='order-items-list'),
    # path('orders/<int:orderId>/', OrderItemDetailView.as_view(), name='order-item-detail'),

]

