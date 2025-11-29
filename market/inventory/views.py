from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import ProductForm
from .models import Product
from .filters import ProductFilter

def products_view(request):
    products = Product.objects.all()
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
    return render(request, 'inventory/products.html', {'products': products, 'filter': product_filter})


def product_detail_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'inventory/product_detail.html', {'product': product})

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