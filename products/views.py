from sqlite3 import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404, redirect
from django.urls import reverse_lazy
from .models import Product, Category, Review
from django.db.models import Sum, Avg
from orders.models import OrderItem
from django.contrib.auth.decorators import login_required
from .forms import ReviewForm
from django.contrib import messages
from .forms import ProductForm
from django.views.generic import DeleteView

def product_list(request):
    category_id = request.GET.get('category')
    if category_id:
        products = Product.objects.filter(category_id=category_id)
    else:
        products = Product.objects.all()

    categories = Category.objects.all()

    most_purchased = (
        Product.objects.annotate(total_sales=Sum("orderitem__quantity"))
        .order_by("-total_sales")[:5]
    )

    best_rated = (
        Product.objects.annotate(avg_rating=Avg("reviews__rating"))
        .order_by("-avg_rating")[:5]
    )

    featured_products = list(most_purchased) + list(best_rated)

    return render(request, "products/product_list.html", {
        "products": products,
        "categories": categories,
        "featured_products": featured_products,
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    reviews = product.reviews.all()
    return render(request, 'products/product_detail.html', {
        'product': product,
        'reviews': reviews
    })
    
def category_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.all()
    return render(request, 'products/category_detail.html', {
        'category': category,
        'products': products,
    })

def review_edit(request, pk):
    review = get_object_or_404(Review, pk=pk, user=request.user)
    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect("product_detail", pk=review.product.id)
    else:
        form = ReviewForm(instance=review)
    return render(request, "products/review_edit.html", {"form": form, "review": review})

def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk)

    if review.user == request.user or request.user.is_staff:
        review.delete()
        messages.success(request, "Reseña eliminada correctamente.")
    else:
        messages.error(request, "No tienes permiso para eliminar esta reseña.")

    return redirect("product_detail", pk=review.product.id)

@login_required
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("product_list") 
    else:
        form = ProductForm()
    return render(request, "products/product_form.html", {"form": form})

@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect("product_detail", pk=product.id)
    else:
        form = ProductForm(instance=product)
    return render(request, "products/product_form.html", {"form": form, "product": product})

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if not request.user.is_staff:
        messages.error(request, "No tienes permiso para eliminar productos.")
        return redirect("product_detail", product_id=product.id)

    product.delete()
    messages.success(request, "Producto eliminado correctamente.")
    return redirect("product_list")  

@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    reviews = product.reviews.all()

    if request.method == 'POST' and request.user.is_authenticated and not request.user.is_staff:
        form = ReviewForm(request.POST)
        if form.is_valid():
            existing_review = Review.objects.filter(product=product, user=request.user).first()
            if existing_review:
                messages.error(request, "Ya has registrado una reseña para este producto.")
            else:
                try:
                    new_review = form.save(commit=False)
                    new_review.user = request.user
                    new_review.product = product
                    new_review.save()
                    messages.success(request, "Reseña registrada correctamente.")
                    return redirect('product_detail', pk=pk)
                except IntegrityError:
                    messages.error(request, "Error al guardar la reseña. Ya existe una registrada.")
    else:
        form = ReviewForm()

    return render(request, 'products/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'form': form
    })
        
class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('product_list')