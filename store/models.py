from django.db import models
from django.contrib.auth.models import User


# ================= DANH MỤC =================
class Category(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


# ================= SẢN PHẨM =================
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='products/')
    price = models.IntegerField()
    quantity = models.IntegerField()
    note = models.TextField(blank=True)

    def __str__(self):
        return self.name


# ================= ĐƠN HÀNG =================
class Order(models.Model):

    PAYMENT_CHOICES = (
        ('cod', 'Thanh toán khi nhận hàng'),
        ('bank', 'Chuyển khoản trước'),
    )

    customer_name = models.CharField(max_length=200)
    address = models.TextField()

    total_price = models.IntegerField(default=0)

    note = models.TextField(blank=True, null=True)

    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_CHOICES,
        default='cod'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    is_prepared = models.BooleanField(default=False)

    def __str__(self):
        return f"Đơn {self.id} - {self.customer_name}"


# ================== CHI TIẾT ĐƠN ==================
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


# ================== THÔNG BÁO ==================
class Notification(models.Model):
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.message

# ================== CHAT ==================
class ChatMessage(models.Model):
    sender = models.CharField(max_length=20)  # "admin" hoặc "customer"
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}: {self.message[:20]}"


class ChatSetting(models.Model):
    is_open = models.BooleanField(default=True)

    def __str__(self):
        return f"Chat open: {self.is_open}"