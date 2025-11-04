from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib import messages
from django.utils import timezone
from .models import Libro, Categoria, Prestamo
from .google_books import GoogleBooksAPI

def index(request):
    libros_destacados = Libro.objects.filter(estado='Disponible')[:6]
    total_libros = Libro.objects.count()
    total_disponibles = Libro.objects.filter(estado='Disponible').count()
    
    context = {
        'libros_destacados': libros_destacados,
        'total_libros': total_libros,
        'total_disponibles': total_disponibles,
        'user': request.user,
    }
    return render(request, 'biblioteca/index.html', context)

def libro_list(request):
    libros = Libro.objects.all()
    categorias = Categoria.objects.all()
    
    context = {
        'libros': libros,
        'categorias': categorias,
        'user': request.user,
    }
    return render(request, 'biblioteca/libro_list.html', context)

def libro_detail(request, id):
    libro = get_object_or_404(Libro, id=id)
    context = {
        'libro': libro,
        'user': request.user,
    }
    return render(request, 'biblioteca/libro_detail.html', context)

def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('/')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def custom_logout(request):
    auth_logout(request)
    return redirect('/')

@login_required
def importar_libros(request):
    if request.method == 'POST':
        query = request.POST.get('query', '').strip()
        max_results = int(request.POST.get('max_results', 5))
        
        if not query:
            messages.error(request, 'Por favor ingresa un término de búsqueda')
            return redirect('importar_libros')
        
        api = GoogleBooksAPI()
        resultados = api.buscar_libros(query, max_results)
        
        if resultados and 'items' in resultados:
            libros_importados = 0
            for item in resultados['items'][:max_results]:
                libro = api.importar_libro_desde_api(item)
                if libro:
                    libros_importados += 1
            
            if libros_importados > 0:
                messages.success(request, f'✅ Se importaron {libros_importados} libros correctamente')
            else:
                messages.info(request, 'No se pudieron importar nuevos libros (posiblemente ya existen)')
        else:
            messages.warning(request, 'No se encontraron libros con esos criterios')
        
        return redirect('libro_list')
    
    return render(request, 'biblioteca/importar_libros.html')

@login_required
def reservar_libro(request, id):
    libro = get_object_or_404(Libro, id=id)
    
    if libro.estado != 'Disponible' or libro.stock < 1:
        messages.error(request, 'Este libro no está disponible para reserva')
        return redirect('libro_detail', id=id)
    
    reserva_existente = Prestamo.objects.filter(
        usuario=request.user, 
        libro=libro,
        estado='Activo'
    ).exists()
    
    if reserva_existente:
        messages.warning(request, 'Ya tienes una reserva activa para este libro')
        return redirect('libro_detail', id=id)
    
    Prestamo.objects.create(
        libro=libro,
        usuario=request.user,
        estado='Activo'
    )
    
    libro.stock -= 1
    if libro.stock == 0:
        libro.estado = 'Prestado'
    libro.save()
    
    messages.success(request, f'✅ ¡Libro "{libro.titulo}" reservado exitosamente!')
    return redirect('mis_reservas')

@login_required
def mis_reservas(request):
    reservas = Prestamo.objects.filter(usuario=request.user, estado='Activo')
    
    context = {
        'reservas': reservas,
        'user': request.user,
    }
    return render(request, 'biblioteca/mis_reservas.html', context)

@login_required
def cancelar_reserva(request, id):
    reserva = get_object_or_404(Prestamo, id=id, usuario=request.user, estado='Activo')
    libro = reserva.libro
    
    # Restaurar stock del libro
    libro.stock += 1
    if libro.estado == 'Prestado':
        libro.estado = 'Disponible'
    libro.save()
    
    # Cambiar estado de la reserva
    reserva.estado = 'Devuelto'
    reserva.save()
    
    messages.success(request, f'❌ Reserva de "{libro.titulo}" cancelada exitosamente')
    return redirect('mis_reservas')

def register_demo(request):
    """Vista demo de registro que redirige al login"""
    if request.method == 'POST':
        # En un demo, cualquier POST redirige al login
        messages.info(request, 'Esta es una versión demo. Usa las credenciales proporcionadas.')
        return redirect('login')
    
    # Mostrar template de registro demo
    return render(request, 'biblioteca/register.html')
