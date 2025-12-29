from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import ProductForm
from .models import Product, Cart
from .filters import ProductFilter
from django.core.paginator import Paginator
from django.db.models import Avg
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def products_view(request):
    products = Product.objects.all().order_by('-id')
    product_filter = ProductFilter(request.GET, queryset=products)
    products = product_filter.qs
    f = product_filter.form
    if 'name' in f.fields:
        f.fields['name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Search name'})
    if 'unit' in f.fields:
        f.fields['unit'].widget.attrs.update({'class': 'form-select'})
    if 'min_price' in f.fields:
        f.fields['min_price'].widget.attrs.update({'class': 'form-control form-control-sm', 'id': 'id_min_price', 'step': '0.01'})
    if 'max_price' in f.fields:
        f.fields['max_price'].widget.attrs.update({'class': 'form-control form-control-sm', 'id': 'id_max_price', 'step': '0.01'})
    if 'min_quantity' in f.fields:
        f.fields['min_quantity'].widget.attrs.update({'class': 'form-control form-control-sm', 'id': 'id_min_quantity', 'step': '0.01'})
    if 'max_quantity' in f.fields:
        f.fields['max_quantity'].widget.attrs.update({'class': 'form-control form-control-sm', 'id': 'id_max_quantity', 'step': '0.01'})
    
    paginator = Paginator(products, 4)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    elided_page_range = paginator.get_elided_page_range(
    number=page_obj.number,
    on_each_side=2,
    on_ends=1)
    
    for product in page_obj:
        avg = product.ratings.aggregate(avg=Avg('value'))['avg']
        if avg is not None:
            product.avg_rating = round(avg, 1)
            product.rating_count = int(round(avg))
            product.has_rating = True
        else:
            product.avg_rating = 0
            product.rating_count = 0
            product.has_rating = False
    
    return render(request, 'inventory/products.html', {'products': page_obj, 'filter': product_filter, 'page_numbers': elided_page_range})


def product_detail_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST' and request.user.is_authenticated:
        rating_value = int(request.POST.get('rating'))
        if 1 <= rating_value <= 5:
            
            Rating.objects.update_or_create(product=product, user=request.user, defaults={'value': rating_value})
    avg = product.ratings.aggregate(avg=Avg('value'))['avg']
    avg_rating = round(avg, 2) if avg is not None else None
    user_rating = None
    if request.user.is_authenticated:
        user_rating = product.ratings.filter(user=request.user).first()

    return render(request, 'inventory/product_detail.html', {'product': product, 'avg_rating': avg_rating, 'user_rating': user_rating})

@login_required
def add_product_view(request):
    form = ProductForm()
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.save()
            messages.success(request, "Product has been added")
            return redirect("inventory:products")
    return render(request, 'inventory/add_product.html', {'form': form, 'title': 'Add a Product', 'submit_label': 'Add'})


@login_required
def edit_product_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(instance=product)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product has been updated')
            return redirect('inventory:products')
    return render(request, 'inventory/add_product.html', {'form': form, 'title': 'Edit Product', 'submit_label': 'Save'})


@login_required
def delete_product_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product has been deleted')
        return redirect('inventory:products')
    return render(request, 'inventory/confirm_delete.html', {'object': product})


@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user, status=Cart.Status.IN_CART).select_related('product')
    updated = False
    for item in cart_items:
        if item.quantity > item.product.quantity:
            item.quantity = item.product.quantity
            item.save()
            updated = True
        item.subtotal = item.product.unit_price * item.quantity
    if updated:
        messages.warning(request, 'Some quantities were adjusted due to stock changes.')
    total = sum(item.subtotal for item in cart_items)
    return render(request, 'inventory/cart.html', {'cart_items': cart_items, 'total': total})


@login_required
def add_to_cart_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if product.quantity <= 0:
        messages.error(request, f'{product.name} is out of stock')
        return redirect('inventory:products')
    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product,
        status=Cart.Status.IN_CART,
        defaults={'quantity': 1}
    )
    if not created:
        if cart_item.quantity >= product.quantity:
            messages.error(request, f'Cannot add more {product.name}, not enough stock')
            return redirect('inventory:products')
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f'{product.name} added to cart')

    try:
        from_email = settings.EMAIL_HOST_USER
        to_email = request.user.email
        
        if not to_email:
            logger.warning(f"Користувач {request.user.username} не має email адреси")
        elif not from_email:
            logger.warning("EMAIL_HOST_USER не налаштований")
        else:
            message = f'Ви додали товар "{product.name}" в кошик.\n\nЦіна: {product.unit_price} / {product.get_unit_display()}\nКількість: {cart_item.quantity}'
            send_mail(
                "Товар додано в кошик",
                message,
                from_email,
                [to_email],
                fail_silently=False, 
            )
            logger.info(f"Email спроба для користувача {request.user.email}")
    except Exception as e:
        logger.error(f"Помилка при відправці email: {str(e)}", exc_info=True)
    
    return redirect('inventory:products')


@login_required
def remove_from_cart_view(request, pk):
    cart_item = get_object_or_404(Cart, pk=pk, user=request.user, status=Cart.Status.IN_CART)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'{product_name} removed from cart')
    return redirect('inventory:cart')


@login_required
def update_cart_quantity_view(request, pk):
    if request.method == 'POST':
        cart_item = get_object_or_404(Cart.objects.select_related('product'), pk=pk, user=request.user, status=Cart.Status.IN_CART)
        try:
            new_quantity = int(request.POST.get('quantity', 1))
            if new_quantity < 1:
                messages.error(request, 'Quantity must be at least 1')
            elif new_quantity > cart_item.product.quantity:
                messages.error(request, f'Only {cart_item.product.quantity} available')
            else:
                cart_item.quantity = new_quantity
                cart_item.save()
                messages.success(request, 'Quantity updated')
        except ValueError:
            messages.error(request, 'Invalid quantity')
    return redirect('inventory:cart')


@login_required
def purchase_view(request):
    if request.method == 'POST':
        cart_items = Cart.objects.filter(user=request.user, status=Cart.Status.IN_CART).select_related('product')
        insufficient_stock = []
        for item in cart_items:
            if item.quantity > item.product.quantity:
                insufficient_stock.append(item.product.name)
        if insufficient_stock:
            messages.error(request, f'Insufficient stock for: {", ".join(insufficient_stock)}. Please update quantities.')
            return redirect('inventory:cart')
        
        
        for item in cart_items:
            item.product.quantity -= item.quantity
            item.product.save()
            item.delete()  
        
        messages.success(request, 'Purchase completed successfully')
    return redirect('inventory:cart')