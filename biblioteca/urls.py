from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('libros/', views.libro_list, name='libro_list'),
    path('libros/<int:id>/', views.libro_detail, name='libro_detail'),
    path('importar-libros/', views.importar_libros, name='importar_libros'),
    path('mis-reservas/', views.mis_reservas, name='mis_reservas'),
    path('register/', views.register_demo, name='register'),
    
    # URLs de autenticación CORREGIDAS
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
]
