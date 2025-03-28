from django.urls import path
from .views import (user_login, user_logout, home,
    admin_dashboard, shopkeeper_dashboard,
    add_product, edit_product, delete_product, product_list, record_sale,
    sales_report, transaction_list
)

urlpatterns = [
    # Authentication Routes
    path('', home, name='home'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),

    # Dashboard Routes
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    path('shopkeeper_dashboard/', shopkeeper_dashboard, name='shopkeeper_dashboard'),

    # Product Management Routes
    path('products/', product_list, name='product_list'),
    path('products/add/', add_product, name='add_product'),
    path('products/edit/<int:product_id>/', edit_product, name='edit_product'),
    path('products/delete/<int:product_id>/', delete_product, name='delete_product'),
    path('sales/record/', record_sale, name='record_sale'),
    path('reports/', sales_report, name='reports_view'),
    path("transactions/", transaction_list, name="transaction_list"),
]
