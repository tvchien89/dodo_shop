from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),

    # ❌ ĐÃ XÓA create_order vì không tồn tại trong views.py

    path('order/<int:product_id>/', views.place_order, name='place_order'),
    path('checkout/', views.checkout, name='checkout'),
    path('cart/', views.cart_view, name='cart'),
    path('chat/get/', views.get_chat, name='get_chat'),
    path('chat/send/', views.send_chat, name='send_chat'),
    path('chat/toggle/', views.toggle_chat, name='toggle_chat'),
    path('chat/clear/', views.clear_chat),

    # ✅ THÊM: Đánh dấu hoàn thành đơn hàng
    path('done/<int:order_id>/', views.mark_done, name='mark_done'),

    # ===== LOGIN / LOGOUT ADMIN =====
    path('login/', auth_views.LoginView.as_view(
        template_name='store/login.html'
    ), name='login'),

    path('logout/', auth_views.LogoutView.as_view(
        next_page='store:home'
    ), name='logout'),
]