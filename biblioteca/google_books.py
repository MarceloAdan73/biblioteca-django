import requests
import json
from django.core.files.base import ContentFile
from django.core.files.temp import NamedTemporaryFile
from biblioteca.models import Libro, Autor, Categoria
import urllib.request
import os

class GoogleBooksAPI:
    BASE_URL = "https://www.googleapis.com/books/v1/volumes"
    
    def __init__(self):
        self.session = requests.Session()
    
    def buscar_libros(self, query, max_results=10):
        """
        Busca libros en Google Books API
        """
        params = {
            'q': query,
            'maxResults': max_results,
            'printType': 'books'
        }
        
        try:
            response = self.session.get(self.BASE_URL, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error en la API: {e}")
            return None
    
    def importar_libro_desde_api(self, book_data):
        """
        Importa un libro desde los datos de la API a la base de datos
        """
        try:
            volume_info = book_data.get('volumeInfo', {})
            
            # Verificar si el libro ya existe por ISBN
            isbns = volume_info.get('industryIdentifiers', [])
            for isbn_info in isbns:
                if isbn_info.get('type') in ['ISBN_13', 'ISBN_10']:
                    isbn = isbn_info.get('identifier')
                    if Libro.objects.filter(ISBN=isbn).exists():
                        print(f"Libro con ISBN {isbn} ya existe")
                        return None
            
            # Crear o obtener autores
            autores = []
            for author_name in volume_info.get('authors', ['Autor Desconocido']):
                autor, created = Autor.objects.get_or_create(
                    nombre=author_name,
                    defaults={
                        'nacionalidad': 'Desconocida',
                        'biografia': f'Autor del libro "{volume_info.get("title", "")}"'
                    }
                )
                autores.append(autor)
            
            # Crear o obtener categorías
            categorias = []
            for category_name in volume_info.get('categories', ['General']):
                categoria, created = Categoria.objects.get_or_create(
                    nombre=category_name[:50],
                    defaults={
                        'descripcion': f'Libros de {category_name}',
                        'color': self._generar_color_aleatorio()
                    }
                )
                categorias.append(categoria)
            
            # Determinar ISBN
            isbn = ""
            for isbn_info in isbns:
                if isbn_info.get('type') == 'ISBN_13':
                    isbn = isbn_info.get('identifier')
                    break
                elif isbn_info.get('type') == 'ISBN_10' and not isbn:
                    isbn = isbn_info.get('identifier')
            
            # Crear el libro
            libro = Libro.objects.create(
                titulo=volume_info.get('title', 'Sin título')[:200],
                ISBN=isbn,
                descripcion=volume_info.get('description', 'Sin descripción disponible.')[:1000],
                estado='Disponible',
                stock=1
            )
            
            # Agregar relaciones ManyToMany
            libro.autores.set(autores)
            libro.categorias.set(categorias)
            
            # Descargar y guardar portada
            image_links = volume_info.get('imageLinks', {})
            thumbnail_url = image_links.get('thumbnail') or image_links.get('smallThumbnail')
            
            if thumbnail_url:
                try:
                    thumbnail_url = thumbnail_url.replace('http://', 'https://')
                    thumbnail_url = thumbnail_url.replace('&edge=curl', '')
                    
                    response = self.session.get(thumbnail_url, timeout=10)
                    if response.status_code == 200:
                        filename = f"portada_{libro.id}.jpg"
                        libro.portada.save(filename, ContentFile(response.content), save=True)
                        print(f"Portada descargada para: {libro.titulo}")
                except Exception as e:
                    print(f"Error descargando portada: {e}")
            
            libro.save()
            print(f"✅ Libro importado: {libro.titulo}")
            return libro
            
        except Exception as e:
            print(f"❌ Error importando libro: {e}")
            return None
    
    def _generar_color_aleatorio(self):
        import random
        colors = ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899']
        return random.choice(colors)
