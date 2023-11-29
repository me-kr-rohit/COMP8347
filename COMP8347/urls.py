"""
URL configuration for COMP8347 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path

from ForexTrade import views
from ForexTrade.views import RegisterView, login_view, home_view, get_exchange_rate, trend, \
    timeseries_view, Payment_History, account_settings
from ForexTrade.views import RegisterView, login_view, home_view, MyAccountView, get_exchange_rate, trend, \
    timeseries_view, Payment_History, save_changes, qtrend
from ForexTrade.views import payment_view, payment_success

urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('about/', views.about, name='about'),
    path('faq/', views.faq, name='faq'),
    path('offer/', views.offers, name='offers'),
    path('contact/', views.contact, name='contactUs'),
    path('account/settings/', account_settings, name='account_settings'),

    path('get_exchange_rate/', get_exchange_rate, name='get_exchange_rate'),
    path('trend/', views.trend, name='trend'),
    path('timeseries_view/', views.timeseries_view, name='timeseries_view'),
    path('payment_view/', views.payment_view, name='payment_view'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('Payment_History/', Payment_History, name='Payment_History'),
    path('save_changes/', save_changes, name='save_changes'),
    path('qtrend/', views.qtrend, name='qtrend'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
