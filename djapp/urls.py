from django.urls import path
from djapp import views

app_name = 'djapp'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('order-history/', views.order_history, name='history'),
    path('billing-history/', views.billing_history, name='billing_history'),
    path('blank-view/', views.blank_view, name='blank'),
    path('process-label/', views.process_single_label, name='process_label'),
    path('invoice/', views.invoice_view, name='invoice'),
    path('get-started/', views.guide, name='guide'),
    path('faq/', views.faq, name='faq'),
    path('maintenance/', views.maintenance_view, name='maintain'),
    path('contact-us/', views.contact_us, name='contact'),
    path('terms-and-conditions/', views.term_and_condition, name='tc'),
    path('pricing.html/', views.pricing, name='pricing'),
    path('add-credit/', views.add_balance, name='add_balance'),
    path('login/', views.login_views, name='login'),
    path('forgotpassword/', views.forgotpassword_views, name='forgotpassword'),
    path('verifypassword/', views.verifypassword_views, name='verifypassword'),
    path('signup/', views.signup_views, name='signup'),
    path('logout/', views.logout, name='logout'),
    path('500/', views.custom_500_view, name='500'),
    path('single-label/', views.single_label, name='single_label'),
]
