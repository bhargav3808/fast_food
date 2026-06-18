from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, CartItem, Category, Cart, DeliveryAddress, Order, Delivery, DeliveryPerson, OrderItem
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from .forms import DeliveryAddressForm
import io


@login_required(login_url="login")
def place_order(request):
    cart_obj = get_object_or_404(Cart, user=request.user, active=True)
    cart_items = cart_obj.items.select_related('product').all()

    if not cart_items:
        messages.error(request, "Your cart is empty.")
        return redirect("cart")

    # Get delivery address
    delivery_address_id = request.POST.get("delivery_address")
    if not delivery_address_id:
        messages.error(request, "Please select a delivery address.")
        return redirect("checkout")
    
    try:
        delivery_address = DeliveryAddress.objects.get(id=delivery_address_id, user=request.user)
    except DeliveryAddress.DoesNotExist:
        messages.error(request, "Invalid delivery address.")
        return redirect("checkout")

    # Calculate total price
    total_price = cart_obj.total_price

    # Create Order
    order = Order.objects.create(
        user=request.user,
        cart=cart_obj,
        total=total_price,
        delivery_address=delivery_address
    )

    # Create OrderItems from CartItems
    for cart_item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            quantity=cart_item.quantity,
            price=cart_item.product.price
        )

    # Create Delivery record
    from datetime import timedelta
    estimated_time = timezone.now() + timedelta(hours=1)  # 1 hour estimated delivery
    
    delivery = Delivery.objects.create(
        order=order,
        status='pending',
        estimated_delivery_time=estimated_time
    )

    # ---- Generate PDF invoice ----
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    p.setFont("Helvetica-Bold", 18)
    p.drawString(50, 750, f"Invoice for Order #{order.id}")

    p.setFont("Helvetica", 12)
    p.drawString(50, 720, f"Customer: {request.user.username}")
    p.drawString(50, 700, f"Delivery Address: {delivery_address.street_address}, {delivery_address.city}")
    p.drawString(50, 680, "Items:")

    y = 660
    for item in cart_items:
        line = f"{item.product.name} - Qty: {item.quantity} - ₹{item.product.price}"
        p.drawString(60, y, line)
        y -= 20

    p.drawString(50, y - 20, f"Total Amount: ₹{total_price}")
    p.drawString(50, y - 40, f"Order Status: {order.status}")
    p.drawString(50, y - 60, f"Delivery Status: {delivery.get_status_display()}")

    p.showPage()
    p.save()

    buffer.seek(0)

    # ---- Clear cart after placing order ----
    cart_obj.items.all().delete()
    cart_obj.active = False
    cart_obj.save()

    messages.success(request, "Order placed successfully! You can track your delivery now.")

    # ---- Return invoice PDF ----
    response = HttpResponse(buffer, content_type="application/pdf")
    response['Content-Disposition'] = f'attachment; filename="invoice_order_{order.id}.pdf"'
    return response

def home(request):
    categories = Category.objects.all() if hasattr(Category, 'objects') else []
    featured = Product.objects.filter(available=True)[:8] if hasattr(Product, 'objects') else []
    return render(request, "food_app/index.html", {"categories": categories, "products": featured})

def product_list(request):
    # show all products grouped by category
    categories = Category.objects.prefetch_related('products').all()
    return render(request, "food_app/menu.html", {"categories": categories})

def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.filter(available=True)
    return render(request, "food_app/categories.html", {"category": category, "products": products})

def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, "food_app/product_detail.html", {"product": product})

@login_required(login_url="login")
def cart(request):
    # find active cart for user or create one
    cart_obj, created = Cart.objects.get_or_create(user=request.user, active=True)
    cart_items = cart_obj.items.select_related('product').all()
    total_price = cart_obj.total_price if cart_obj else 0
    return render(request, "food_app/cart.html", {
        "cart_items": cart_items,
        "total_price": total_price
    })

@login_required(login_url="login")
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart_obj, created = Cart.objects.get_or_create(user=request.user, active=True)
    cart_item, created = CartItem.objects.get_or_create(cart=cart_obj, product=product)
    if not created:
        cart_item.quantity += 1
    cart_item.save()
    messages.success(request, "Item added to cart!")
    return redirect(request.META.get("HTTP_REFERER", "menu"))


@login_required(login_url="login")
def remove_from_cart(request, product_id):
    cart_obj = get_object_or_404(Cart, user=request.user, active=True)
    item = get_object_or_404(CartItem, cart=cart_obj, product_id=product_id)
    item.delete()
    messages.success(request, "Item removed!")
    return redirect("cart")

@login_required(login_url="login")
def checkout(request):
    cart_obj = get_object_or_404(Cart, user=request.user, active=True)
    cart_items = cart_obj.items.select_related('product').all()
    total_price = cart_obj.total_price
    delivery_addresses = request.user.delivery_addresses.all()
    default_address = delivery_addresses.filter(is_default=True).first()
    
    return render(request, "food_app/checkout.html", {
        "cart_items": cart_items,
        "total_price": total_price,
        "delivery_addresses": delivery_addresses,
        "default_address": default_address
    })

def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password")
    return render(request, "food_app/login.html")

def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect("home")

def user_register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect("register")
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Registration successful! Please log in.")
        return redirect("login")
    return render(request, "food_app/register.html")


# ============ DELIVERY SYSTEM VIEWS ============

@login_required(login_url="login")
def delivery_addresses(request):
    """List user's delivery addresses"""
    addresses = request.user.delivery_addresses.all()
    return render(request, "food_app/delivery_addresses.html", {"addresses": addresses})


@login_required(login_url="login")
def add_delivery_address(request):
    """Add new delivery address"""
    if request.method == "POST":
        form = DeliveryAddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            
            # If marking as default, unmark other addresses
            if address.is_default:
                DeliveryAddress.objects.filter(user=request.user, is_default=True).update(is_default=False)
            
            address.save()
            messages.success(request, "Delivery address added successfully!")
            return redirect("delivery_addresses")
    else:
        form = DeliveryAddressForm()
    
    return render(request, "food_app/add_delivery_address.html", {"form": form})


@login_required(login_url="login")
def edit_delivery_address(request, address_id):
    """Edit delivery address"""
    address = get_object_or_404(DeliveryAddress, id=address_id, user=request.user)
    
    if request.method == "POST":
        form = DeliveryAddressForm(request.POST, instance=address)
        if form.is_valid():
            updated_address = form.save(commit=False)
            
            if updated_address.is_default:
                DeliveryAddress.objects.filter(user=request.user, is_default=True).exclude(id=address.id).update(is_default=False)
            
            updated_address.save()
            messages.success(request, "Delivery address updated successfully!")
            return redirect("delivery_addresses")
    else:
        form = DeliveryAddressForm(instance=address)
    
    return render(request, "food_app/edit_delivery_address.html", {"form": form, "address": address})


@login_required(login_url="login")
def delete_delivery_address(request, address_id):
    """Delete delivery address"""
    address = get_object_or_404(DeliveryAddress, id=address_id, user=request.user)
    address.delete()
    messages.success(request, "Delivery address deleted!")
    return redirect("delivery_addresses")


@login_required(login_url="login")
def order_detail(request, order_id):
    """View order details and delivery tracking"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = order.items.all()
    delivery = getattr(order, 'delivery', None)
    
    return render(request, "food_app/order_detail.html", {
        "order": order,
        "order_items": order_items,
        "delivery": delivery
    })


@login_required(login_url="login")
def order_history(request):
    """View user's order history"""
    orders = request.user.order_set.all().order_by('-created_at')
    
    return render(request, "food_app/order_history.html", {
        "orders": orders
    })


@login_required(login_url="login")
def track_order(request, order_id):
    """Real-time order tracking"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    delivery = getattr(order, 'delivery', None)
    
    context = {
        "order": order,
        "delivery": delivery,
    }
    
    if delivery and delivery.delivery_person:
        context["delivery_person"] = delivery.delivery_person
        context["current_location"] = {
            "latitude": delivery.delivery_person.current_latitude,
            "longitude": delivery.delivery_person.current_longitude,
        }
    
    return render(request, "food_app/track_order.html", context)


@login_required(login_url="login")
def delivery_status_api(request, order_id):
    """API endpoint for delivery status (AJAX)"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    delivery = getattr(order, 'delivery', None)
    
    if not delivery:
        return JsonResponse({"error": "No delivery found"}, status=404)
    
    data = {
        "status": delivery.status,
        "status_display": delivery.get_status_display(),
        "updated_at": delivery.updated_at.isoformat(),
        "estimated_delivery_time": delivery.estimated_delivery_time.isoformat() if delivery.estimated_delivery_time else None,
    }
    
    if delivery.delivery_person:
        data["delivery_person"] = {
            "name": delivery.delivery_person.user.get_full_name() or delivery.delivery_person.user.username,
            "phone": delivery.delivery_person.phone,
            "vehicle_info": delivery.delivery_person.vehicle_info,
            "current_latitude": delivery.delivery_person.current_latitude,
            "current_longitude": delivery.delivery_person.current_longitude,
        }
    
    return JsonResponse(data)
