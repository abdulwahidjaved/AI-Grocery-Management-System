from django.db import models
from decimal import Decimal

class Product(models.Model):
    name = models.CharField(max_length=100, default="")
    description = models.CharField(max_length=200, default="")
    price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    quantity = models.IntegerField(default=0)
    image = models.ImageField(upload_to="products/", blank=True, null=True)

    def __str__(self):
        return self.name
    
class Staff(models.Model):
    firstName = models.CharField(max_length=10, default="")
    lastName = models.CharField(max_length=10, default="")
    age = models.IntegerField(default=0)
    address = models.TextField(max_length=100, default="")
    image = models.ImageField(upload_to="staff/", blank=True, null=True)
    phoneNumber = models.CharField(max_length=15, default="")
    role = models.CharField(max_length=20, default="")

    def __str__(self):
        return f"{self.firstName} {self.lastName}" 
    
class Customer(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Bill(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bill #{self.id} - {self.customer.name if self.customer else 'Guest'} - {self.total_amount}"

class BillItem(models.Model):
    bill = models.ForeignKey(Bill, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey("Product", on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=200)            # snapshot name
    product_price = models.DecimalField(max_digits=12, decimal_places=2)  # snapshot price
    quantity = models.PositiveIntegerField()
    total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
