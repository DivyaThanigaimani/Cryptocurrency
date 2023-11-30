from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
from .views import glossary_view,CreateStripeCheckoutSessionView, SuccessView

urlpatterns = [
    path('', views.homepage, name=""),
    path('register', views.register, name="register"),
    path('my-login', views.my_login, name="my-login"),
    path('dashboard', views.stocks, name="dashboard"),
    path('user-logout', views.user_logout, name="user-logout"),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('contact_us/', views.contact_us, name='contact_us'),
    path('glossary/', glossary_view, name='glossary'),
    path('payment-history/', views.payment_history, name='payment_history'),
    path('exchange_view',views.exchange_view,name="exchange_view"),
    path("create-checkout-session", CreateStripeCheckoutSessionView.as_view(),
         name="create-checkout-session"),
    path("success/", SuccessView.as_view(), name="success"),
path('convert_currency/<str:amount>/<str:from_currency>/<str:to_currency>/', views.convert_currency, name='convert_currency'),
    # path('monthly_stock_data',views.monthly_stock_data,name='monthly_stock_data'),
    path('stockinfo/<path:stockname>/',views.stockinfo,name='stockinfo'),
    # path('data',views.data,name='data'),
    path('stocks',views.stocks,name='stocks'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
