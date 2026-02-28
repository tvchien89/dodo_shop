from django.contrib import admin
from .models import Category, Product, Order, OrderItem, Notification
from .models import ChatMessage, ChatSetting

# ================== ORDER INLINE ==================
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


# ================== ORDER ADMIN ==================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # 👇 Thêm is_prepared vào đây để có dấu tích
    list_display = ('id', 'customer_name', 'total_price', 'is_prepared', 'created_at')

    # 👇 Cho phép tick trực tiếp không cần vào chi tiết
    list_editable = ('is_prepared',)

    # 👇 Có thể lọc theo trạng thái
    list_filter = ('is_prepared', 'created_at')

    inlines = [OrderItemInline]


# ================== REGISTER MODELS ==================
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Notification)


# ================== CUSTOM ADMIN DASHBOARD ==================
admin.site.index_template = "admin/index.html"

original_index = admin.site.index

def custom_admin_index(request, extra_context=None):
    extra_context = extra_context or {}
    extra_context["recent_orders"] = Order.objects.order_by("-created_at")[:10]
    return original_index(request, extra_context=extra_context)

admin.site.index = custom_admin_index
admin.site.register(ChatMessage)
admin.site.register(ChatSetting)