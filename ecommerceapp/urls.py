from django.urls import path
from ecommerceapp import views
from .views import subscribe
from django.views.generic import TemplateView

urlpatterns = [
    path('',views.index,name="index"),
    path('contact',views.contact,name="contact"),
    path('about',views.about,name="about"),
    path('blog',views.blog,name="blog"),
    path('profile',views.profile,name="profile"),
    path('checkout/', views.checkout, name="Checkout"),
    path('handlerequest/', views.handlerequest, name="HandleRequest"),
    path('subscribe/', subscribe, name='subscribe'),
    path('subscribe_success/', TemplateView.as_view(template_name='subscribe_success.html'), name='subscribe_success'),

]