from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Sum, Avg, Count, F, ExpressionWrapper, FloatField
from orders.models import Order, OrderItem
from products.models import Product
from users.models import User
from django.utils import timezone

@staff_member_required
def dashboard_view(request):
    today = timezone.now()
    last_week = today - timezone.timedelta(days=7)

    new_orders = Order.objects.filter(created_at__gte=last_week).count()
    total_income = Order.objects.aggregate(total=Sum("total_amount"))["total"] or 0
    total_users = User.objects.count()

    top_sold = (
        OrderItem.objects.values("product__name")
        .annotate(total=Sum("quantity"))
        .order_by("-total")[:5]
    )

    top_rated = (
        Product.objects.annotate(avg_rating=Avg("reviews__rating"))
        .order_by("-avg_rating")[:5]
        .values("name", "avg_rating")
    )

    for r in top_rated:
        if r["avg_rating"] is None:
            r["avg_rating"] = 0

    return render(request, "dashboard/dashboard.html", {
        "new_orders": new_orders,
        "total_income": total_income,
        "total_users": total_users,
        "top_sold": list(top_sold),
        "top_rated": list(top_rated),
    })
    

def dashboard_data(request):
    range = request.GET.get("range", "weekly")
    today = timezone.now()

    if range == "monthly":
        start_date = today - timezone.timedelta(days=30)
    else:
        start_date = today - timezone.timedelta(days=7)

    top_sold = (
        OrderItem.objects.filter(order__created_at__gte=start_date)
        .values("product__name")
        .annotate(total=Sum("quantity"))
        .order_by("-total")[:5]
    )

    top_rated = (
        Product.objects.annotate(avg_rating=Avg("reviews__rating"))
        .order_by("-avg_rating")[:5]
        .values("name", "avg_rating")
    )

    for r in top_rated:
        if r["avg_rating"] is None:
            r["avg_rating"] = 0


    income_by_category = (
        OrderItem.objects.filter(order__created_at__gte=start_date)
        .annotate(subtotal=ExpressionWrapper(F("price") * F("quantity"), output_field=FloatField()))
        .values("product__category__name")
        .annotate(total=Sum("subtotal"))
        .order_by("-total")[:5]
    )

    formatted_income = [
        {"category": i["product__category__name"], "total": i["total"] or 0}
        for i in income_by_category
    ]

    return JsonResponse({
        "top_sold": list(top_sold),
        "top_rated": list(top_rated),
        "income_by_category": formatted_income,
    })