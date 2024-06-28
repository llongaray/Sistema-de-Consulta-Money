from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.consultas.urls')),
    path('ranking/', include('apps.ranking.urls')),
    path('consulta/', include('apps.vendas.siape.urls'))
]
