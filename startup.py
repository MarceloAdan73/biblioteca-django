import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biblioteca_project.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Crear superusuario si no existe
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@biblioteca.com', 'admin123')
    print("✅ Superusuario 'admin' creado automáticamente")
else:
    print("✅ Superusuario 'admin' ya existe")
