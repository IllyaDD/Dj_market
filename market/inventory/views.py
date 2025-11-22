from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import ProductForm
from .models import Product


def products_view(request):
    products = Product.objects.all()
    return render(request, 'inventory/products.html', {'products': products})


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