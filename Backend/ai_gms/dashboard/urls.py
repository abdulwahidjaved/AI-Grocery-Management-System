from django.urls import path

from dashboard import views

urlpatterns = [

    path("",views.login_view, name="login_view"),

    # Admin
    path("admin/", views.admin, name="admin"),
    path("admin/staff/", views.adminStaff, name="admin/staff"),
    path("admin/reports/", views.adminReports, name="admin/reports"),
    path("admin/products/", views.adminProducts, name="admin/products"),
    path("admin/inventory/", views.adminInventory, name="admin/inventory"),

    # Staff
    path("staff/", views.staff, name="staff"),
    path("staff/billing", views.staffBilling, name="staff/billing"),
    path("staff/customers", views.staffCustomers, name="staff/customers"),
    path("staff/products", views.staffProducts, name="staff/products")
]
