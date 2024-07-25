from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

app_name = "colab"

urlpatterns = [
    path('importar_funcionarios/', views.importar_funcionarios, name='importar_funcionarios'),
    path('import_csv/', views.colab_import_csv, name='import_csv'),
    path('import_money/', views.colab_import_money, name='import_money'),
    path('import_photo/', views.colab_import_photo, name='import_photo'),
    path('ranking/', views.render_ranking, name='render_ranking'),
    path('ranking/data/', views.ranking, name='update_ranking'),
    path('lista-registros/', views.lista_registros, name='lista_registros'),
    path('alterar-status/<int:id>/', views.alterar_status, name='alterar_status'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
