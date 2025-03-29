from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.utils.timezone import now

from .forms import RegisterationForm, LoginForm, ProductForm, SalesForm
from .models import User, Products, Sale



def user_login(request):
    """ Handles user login. """
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user:
                login(request, user)
                return redirect('admin_dashboard' if user.is_admin() else 'shopkeeper_dashboard')

        messages.error(request, "Invalid username or password.")

    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


@login_required
def user_logout(request):
    """ Logs out the current user. """
    logout(request)
    return redirect('home')

@login_required 
def home(request):
    """ Redirects users based on their role. """
    if request.user.is_admin():
        return redirect('admin_dashboard')
    elif request.user.is_shopkeeper():
        return redirect('shopkeeper_dashboard')

    return render(request, 'home.html')


@login_required
def admin_dashboard(request):
    """ Renders the admin dashboard. """
    if not request.user.is_admin():
        messages.error(request, "You are not authorized to access this page.")
        return redirect('home')

    return render(request, 'admin_dashboard.html')


@login_required
def shopkeeper_dashboard(request):
    """ Renders the shopkeeper dashboard. """
    if not request.user.is_shopkeeper():
        messages.error(request, "You are not authorized to access this page.")
        return redirect('home')

    products = Products.objects.all()
    return render(request, 'shopkeeper_dashboard.html', {'products': products})


@login_required
def product_list(request):
    """ Displays a list of all products. """
    products = Products.objects.all()
    return render(request, 'product_list.html', {'products': products})


@login_required
def add_product(request):
    """ Allows a shopkeeper to add a new product. """
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Product added successfully!")
            return redirect('product_list')

    else:
        form = ProductForm()

    return render(request, 'product_form.html', {'form': form})


@login_required
def edit_product(request, product_id):
    """ Allows a shopkeeper to edit an existing product. """
    product = get_object_or_404(Products, id=product_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully!")
            return redirect('product_list')

    else:
        form = ProductForm(instance=product)

    return render(request, 'product_form.html', {'form': form})


@login_required
def delete_product(request, product_id):
    """ Allows a shopkeeper to delete a product. """
    product = get_object_or_404(Products, id=product_id)
    product.delete()
    messages.success(request, "Product deleted successfully!")
    return redirect('product_list')


@login_required
def record_sale(request):
    """ Records a new sale and updates stock accordingly. """
    if request.method == 'POST':
        form = SalesForm(request.POST)
        if form.is_valid():
            sale = form.save(commit=False)

            if sale.product.stock >= sale.quantity:
                try:
                    sale.product.stock -= sale.quantity
                    sale.product.save()
                    sale.save()  # Ensure the sale is recorded
                    messages.success(request, f"Sale recorded: {sale.quantity} x {sale.product.name} at ${sale.selling_price} each")
                    return redirect('shopkeeper_dashboard')

                except Exception as e:
                    messages.error(request, f"Error processing sale: {str(e)}")
            else:
                messages.error(request, f"Not enough stock for {sale.product.name}")

    else:
        form = SalesForm()

    return render(request, 'record_sale.html', {'form': form})


@login_required
def sales_report(request):
    """Generate daily and monthly profit & loss reports based on user input."""
    
    today = now().date()
    
    # Get parameters from request
    selected_date = request.GET.get("date", today.strftime("%Y-%m-%d"))
    selected_month = request.GET.get("month", today.month)
    selected_year = request.GET.get("year", today.year)

    # Convert selected_date to datetime.date object
    try:
        if isinstance(selected_date, str):
            selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
        else:
            selected_date = today  # Default to today if conversion fails
        
        selected_month = int(selected_month)
        selected_year = int(selected_year)
    
    except ValueError:
        selected_date = today
        selected_month = today.month
        selected_year = today.year

    # Daily sales report
    daily_sales_report = (
        Sale.objects
        .filter(sale_date__date=selected_date)
        .values("product__name")
        .annotate(
            total_quantity=Sum("quantity"),
            total_profit=Sum(ExpressionWrapper(
                F("quantity") * (F("selling_price") - F("product__cost_price")),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            ))
        )
    )

    # Monthly sales report
    monthly_sales_report = (
        Sale.objects
        .filter(sale_date__month=selected_month, sale_date__year=selected_year)
        .values("product__name")
        .annotate(
            total_quantity=Sum("quantity"),
            total_profit=Sum(ExpressionWrapper(
                F("quantity") * (F("selling_price") - F("product__cost_price")),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            ))
        )
    )

    total_daily_profit = sum(sale["total_profit"] for sale in daily_sales_report if sale["total_profit"] is not None)
    total_monthly_profit = sum(sale["total_profit"] for sale in monthly_sales_report if sale["total_profit"] is not None)

    return render(request, "reports.html", {
        "daily_sales_report": daily_sales_report,
        "monthly_sales_report": monthly_sales_report,
        "total_daily_profit": total_daily_profit,
        "total_monthly_profit": total_monthly_profit,
        "selected_date": selected_date,
        "selected_month": selected_month,
        "selected_year": selected_year,
    })

    
@login_required
def transaction_list(request):
    """ View all recorded transactions with filtering options. """
    transactions = Sale.objects.select_related("product").order_by("-sale_date")

    customer = request.GET.get('customer', '')
    product_id = request.GET.get('product', '')
    date = request.GET.get('date', '')

    if customer:
        transactions = transactions.filter(customer_details__icontains=customer)
    
    if product_id:
        transactions = transactions.filter(product__id=product_id)

    if date:
        try:
            date_obj = now().strptime(date, "%Y-%m-%d").date()
            transactions = transactions.filter(sale_date__date=date_obj)
        except ValueError:
            pass  # Ignore invalid date input

    products = Products.objects.all()  # For dropdown filter

    return render(request, "transactions.html", {
        "transactions": transactions,
        "products": products,
        "selected_customer": customer,
        "selected_product": product_id,
        "selected_date": date
    })
