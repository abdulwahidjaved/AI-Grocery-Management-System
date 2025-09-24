from django.contrib import admin
from .models import Bill, BillItem, Customer, Product, Staff

admin.site.register(Product)
admin.site.register(Staff)
admin.site.register(Customer)
admin.site.register(Bill)
admin.site.register(BillItem)
