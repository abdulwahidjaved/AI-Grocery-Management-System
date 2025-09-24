from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render
from .models import Product, Staff, Customer, Bill, BillItem
from decimal import Decimal
from django.db import transaction
from django.db.models import Sum, Avg

from django.shortcuts import render, redirect
from .models import Staff

def login_view(request):
    message = ""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Admin login
        if username == "admin" and password == "admin123":
            request.session['user_type'] = 'admin'
            return redirect('/dashboard/admin')  # change to your admin dashboard url

        # Staff login
        staff = Staff.objects.filter(firstName=username).first()
        if staff and password == "staff123":
            request.session['user_type'] = 'staff'
            request.session['staff_id'] = staff.id
            return redirect('/dashboard/staff')  # change to your staff dashboard url

        # Invalid login
        message = "Invalid username or password"

    return render(request, "dashboard/login.html", {"message": message})


# Admin
def admin(request):
    return render(request, "dashboard/admin/admin.html")

def adminStaff(request):
    staffs = Staff.objects.all()  # fetch all products
    return render(request, "dashboard/admin/pages/staff/staff.html", {"staffs": staffs})

from django.db.models.functions import TruncDate

from django.shortcuts import render
from django.db.models import Sum, Avg
from .models import Product, Bill

def adminReports(request):
    # Aggregate data
    total_products = Product.objects.count()
    total_stock = Product.objects.aggregate(total=Sum('quantity'))['total'] or 0
    total_revenue = Bill.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    average_bill = Bill.objects.aggregate(avg=Avg('total_amount'))['avg'] or 0

    # Get recent bills
    bills = Bill.objects.order_by('-created_at')[:10]  # latest 10 bills

    context = {
        "total_products": total_products,
        "total_stock": total_stock,
        "total_revenue": total_revenue,
        "average_bill": average_bill,
        "bills": bills,
    }
    return render(request, "dashboard/admin/pages/reports/reports.html", context)


def adminProducts(request):
    if request.method == "POST":
        action = request.POST.get("action")

        # Upload Product
        if action == "upload":
            name = request.POST.get("name")
            description = request.POST.get("description")
            price = request.POST.get("price")
            quantity = request.POST.get("quantity")
            image = request.FILES.get("image")

            Product.objects.create(
                name=name,
                description=description,
                price=price,
                quantity=quantity,
                image=image,
            )
            messages.success(request, f"Product '{name}' uploaded successfully!")
            return redirect("admin/products")  # URL name

        # Delete Product by name
        elif action == "delete":
            product_name = request.POST.get("product_name")
            try:
                product = get_object_or_404(Product, name=product_name)
                product.delete()
                messages.success(request, f"Product '{product_name}' deleted successfully!")
            except:
                messages.error(request, f"Product '{product_name}' not found!")
            return redirect("admin/products")

    return render(request, "dashboard/admin/pages/products/products.html")

def adminInventory(request):
    products = Product.objects.all()  # fetch all products
    return render(request, "dashboard/admin/pages/inventory/inventory.html", {"products": products})


# Staff
def staff(request):
    return render(request, "dashboard/staff/staff.html")



@transaction.atomic
def staffBilling(request):
    products = Product.objects.all()

    if request.method == "POST":
        # --- customer info ---
        customer_name = (request.POST.get("customer_name") or "").strip()
        customer_phone = (request.POST.get("customer_phone") or "").strip()
        customer_email = (request.POST.get("customer_email") or "").strip()

        # Find existing customer (prefer phone, then email), otherwise create
        customer = None
        if customer_phone:
            customer = Customer.objects.filter(phone=customer_phone).first()
        if not customer and customer_email:
            customer = Customer.objects.filter(email=customer_email).first()
        if not customer:
            customer = Customer.objects.create(
                name=customer_name or "Unknown",
                phone=customer_phone or None,
                email=customer_email or None
            )

        # --- bill creation (temporary total = 0, update later) ---
        bill = Bill.objects.create(customer=customer, total_amount=Decimal('0.00'))

        product_ids = request.POST.getlist("product_id[]")
        quantities = request.POST.getlist("quantity[]")

        bill_total = Decimal('0.00')
        created_items = []

        for i, prod_id in enumerate(product_ids):
            # safely parse qty
            try:
                qty = int(quantities[i])
            except (IndexError, ValueError):
                continue
            if qty <= 0:
                continue

            product = get_object_or_404(Product, id=prod_id)

            # enforce stock limit
            if qty > product.quantity:
                qty = product.quantity

            if qty <= 0:
                continue  # nothing to sell

            item_total = Decimal(str(product.price)) * qty
            bill_total += item_total

            # create BillItem (snapshot name/price)
            bi = BillItem.objects.create(
                bill=bill,
                product=product,
                product_name=product.name,
                product_price=Decimal(str(product.price)),
                quantity=qty,
                total=item_total
            )
            created_items.append(bi)

            # reduce stock and optionally delete when exhausted
            product.quantity -= qty
            if product.quantity <= 0:
                product.delete()           # or product.quantity = 0; product.save()
            else:
                product.save()

        # If no items were created, rollback and show message (optional)
        if not created_items:
            # rollback transaction by raising (or just delete bill)
            bill.delete()
            context = {"products": Product.objects.all(), "error": "No products selected or insufficient stock."}
            return render(request, "dashboard/staff/pages/billing/billing.html", context)

        # update bill total
        bill.total_amount = bill_total
        bill.save()

        # Refresh available products for display after stock update
        products = Product.objects.all()

        # Render page with bill details
        return render(request, "dashboard/staff/pages/billing/billing.html", {
            "products": products,
            "bill_items": bill.items.all(),
            "total_amount": bill.total_amount,
            "customer_name": customer.name,
            "customer_phone": customer.phone,
            "customer_email": customer.email,
            "bill_id": bill.id,
        })

    # GET
    return render(request, "dashboard/staff/pages/billing/billing.html", {"products": products})

def staffCustomers(request):
    # fetch bills with related customer and items (efficient with select_related + prefetch_related)
    bills = Bill.objects.select_related("customer").prefetch_related("items").all().order_by("-created_at")

    return render(request, "dashboard/staff/pages/customers/customers.html", {
        "bills": bills
    })

def staffProducts(request):
    products = Product.objects.all()  # fetch all products
    return render(request, "dashboard/staff/pages/products/products.html", {"products": products})