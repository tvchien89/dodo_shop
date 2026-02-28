from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Product, Category, Order, OrderItem, Notification
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
import json
from django.http import JsonResponse
from .models import ChatMessage, ChatSetting
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required


# ================= HOME =================
def home(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    search = request.GET.get('search')
    category_id = request.GET.get('category')

    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(category__name__icontains=search)
        )

    if category_id:
        products = products.filter(category_id=category_id)

    orders = Order.objects.all().order_by('-id')

    # ✅ Đếm đơn chưa xử lý
    new_orders_count = Order.objects.filter(is_prepared=False).count()

    context = {
        'products': products,
        'categories': categories,
        'search': search,
        'selected_category': category_id,
        'orders': orders,
        'new_orders_count': new_orders_count,
    }

    return render(request, 'store/home.html', context)


# ================= PLACE ORDER =================
def place_order(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1))
        customer_name = request.POST.get("customer_name")
        address = request.POST.get("address")
        note = request.POST.get("note")
        payment_method = request.POST.get("payment_method") or "cod"

        total_price = product.price * quantity

        order = Order.objects.create(
            customer_name=customer_name,
            address=address,
            total_price=total_price,
            note=note,
            payment_method=payment_method
        )

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity
        )

        Notification.objects.create(
            message=f"🛎 Đơn mới từ {customer_name} - {product.name} - SL: {quantity} - Tổng {total_price} VND"
        )

        messages.success(request, "🎉 Đặt hàng thành công! Quán đang chuẩn bị đơn cho bạn.")

        return redirect('store:home')

    return redirect('store:home')


# ================= CHECKOUT (GIỎ HÀNG) =================
def checkout(request):
    if request.method == "POST":
        data = json.loads(request.body)

        order = Order.objects.create(
            customer_name=data["customer_name"],
            address=data["address"],
            note=data.get("note", ""),
            total_price=0,
            payment_method="cod"
        )

        total = 0

        for item in data["cart"]:
            product = Product.objects.get(id=item["id"])

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item["quantity"]
            )

            total += product.price * item["quantity"]

        order.total_price = total
        order.save()

        Notification.objects.create(
            message=f"🛎 Đơn mới từ {order.customer_name} - Tổng {total} VND"
        )

        return JsonResponse({"status": "ok"})


# ================= TOGGLE HOÀN THÀNH =================
@staff_member_required
def mark_done(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # ✅ Đảo trạng thái (bấm lại để bỏ tích)
    order.is_prepared = not order.is_prepared
    order.save()

    return redirect('/admin/')

def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    from .models import Product

    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        total_price += product.price * quantity
        cart_items.append({
            'product': product,
            'quantity': quantity
        })

    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })


# ================= CHAT =================
def get_chat(request):
    messages = ChatMessage.objects.order_by('created_at')
    data = [
        {
            "sender": m.sender,
            "message": m.message
        } for m in messages
    ]

    setting = ChatSetting.objects.first()
    is_open = setting.is_open if setting else True

    return JsonResponse({
        "messages": data,
        "is_open": is_open
    })


def send_chat(request):
    if request.method == "POST":
        data = json.loads(request.body)
        ChatMessage.objects.create(
            sender=data["sender"],
            message=data["message"]
        )
        return JsonResponse({"status": "ok"})



@require_POST
@login_required
def toggle_chat(request):
    if not request.user.is_staff:
        return JsonResponse({"status": "forbidden"})

    setting = ChatSetting.objects.first()
    if not setting:
        setting = ChatSetting.objects.create(is_open=True)

    setting.is_open = not setting.is_open
    setting.save()

    return JsonResponse({
        "status": "ok",
        "is_open": setting.is_open
    })




@staff_member_required
def clear_chat(request):
    from .models import ChatMessage
    ChatMessage.objects.all().delete()
    return JsonResponse({"status": "ok"})