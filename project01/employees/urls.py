from django.urls import path
from django.contrib.auth import views as auth_views
from employees import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='employees/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('access-denied/', views.access_denied, name='access_denied'),
    path('', views.dashboard, name='dashboard'),
]
