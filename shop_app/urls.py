from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('select-role/', views.select_role_view, name='select_role'),
    path('set-role/', views.set_role_view, name='set_role'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('products/', views.manage_products_view, name='manage_products'),
    path('products/add/', views.add_product_view, name='add_product'),
    path('products/edit/<str:product_id>/', views.edit_product_view, name='edit_product'),
    path('products/delete/<str:product_id>/', views.delete_product_view, name='delete_product'),
    path('customers/', views.manage_customers_view, name='manage_customers'),
    path('orders/', views.manage_orders_view, name='manage_orders'),
    path('browse/', views.browse_products_view, name='browse_products'),
    path('my-orders/', views.my_orders_view, name='my_orders'),
    path('my-profile/', views.my_profile_view, name='my_profile'),
    path('my-profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('switch-role/', views.switch_role_view, name='switch_role'),
    path('logout/', views.logout_view, name='logout'),
]
