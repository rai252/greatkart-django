from django.urls import path
from .import views

urlpatterns = [
    path('',views.cart,name='cart'),
    path('subtract_cart/<int:product_id>/', views.subtract_cart, name='subtract_cart'),
    path('add_cart/<int:product_id>/',views.add_cart,name='add_cart'),
    path('remove_cart_item/<int:product_id>/',views.remove_cart_item,name='remove_cart_item'),
]
