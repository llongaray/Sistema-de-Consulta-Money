from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

app_name = "colab"

urlpatterns = [
    path('importar_funcionarios/', views.importar_funcionarios, name='importar_funcionarios'),
    path('import_csv/', views.colab_import_csv, name='import_csv'),
    path('import_manual/', views.colab_import_manual, name='import_manual'),
    path('import_photo/', views.colab_import_photo, name='import_photo'),
    path('import_money_csv/', views.money_import_csv, name='import_money_csv'),
    path('import_money_manual/', views.money_import_manual, name='import_money_manual'),
    path('import_metas/', views.import_metas, name='import_metas'),
    path('', views.render_ranking, name='render_ranking'),
    path('ranking/data/', views.ranking, name='update_ranking'),
    path('lista-registros/', views.lista_registros, name='lista_registros'),
    path('alterar-status/<int:id>/', views.alterar_status, name='alterar_status'),
    path('alterar-status-meta/<int:id>/', views.alterar_status_meta, name='alterar_status_meta'),  # Nova rota adicionada
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
