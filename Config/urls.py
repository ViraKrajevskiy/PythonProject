from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.contrib.auth import get_user_model

def create_admin(request):
    try:
        User = get_user_model()
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', '3003')
            return HttpResponse("Админ создан!")
        return HttpResponse("Уже есть.")
    except Exception as e:
        return HttpResponse(f"Ошибка: {e}")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('init-admin/', create_admin),
    path('', include('Project.urls')), # Подключаем ссылки приложения
]
