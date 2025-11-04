from django.contrib import admin
from .models import Autor, Categoria, Libro, Prestamo, Resena

@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'apellido', 'nacionalidad']
    list_filter = ['nacionalidad']
    search_fields = ['nombre', 'apellido']

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'color']
    search_fields = ['nombre']

@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'ISBN', 'estado', 'stock', 'fecha_creacion']
    list_filter = ['estado', 'categorias', 'autores']
    search_fields = ['titulo', 'ISBN', 'descripcion']
    filter_horizontal = ['autores', 'categorias']
    readonly_fields = ['fecha_creacion']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('titulo', 'ISBN', 'descripcion', 'portada')
        }),
        ('Clasificación', {
            'fields': ('autores', 'categorias')
        }),
        ('Inventario', {
            'fields': ('estado', 'stock', 'fecha_creacion')
        }),
    )

@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = ['libro', 'usuario', 'fecha_prestamo', 'fecha_devolucion', 'estado']
    list_filter = ['estado', 'fecha_prestamo']
    search_fields = ['libro__titulo', 'usuario__username']

@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    list_display = ['libro', 'usuario', 'rating', 'fecha_creacion']
    list_filter = ['rating', 'fecha_creacion']
    search_fields = ['libro__titulo', 'usuario__username']
    readonly_fields = ['fecha_creacion']
