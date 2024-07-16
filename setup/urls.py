from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    #urls apps
    path('', include('apps.consultas.urls')),
    path('', include('apps.usuarios.urls')),
]
