from django.urls import path
from . import views
from .views import glossary_view

urlpatterns = [
    path('', views.homepage, name=""),
    path('register', views.register, name="register"),
    path('my-login', views.my_login, name="my-login"),
    path('dashboard', views.dashboard, name="dashboard"),
    path('user-logout', views.user_logout, name="user-logout"),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('contact_us/', views.contact_us, name='contact_us'),
    path('glossary/', glossary_view, name='glossary'),
    path('payment-history/', views.payment_history, name='payment_history'),
]
