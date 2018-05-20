from django.urls import path

from . import views

app_name = "apuestas"
urlpatterns = [
    path('etapas/crear/',
         views.EtapaCreateView.as_view(),
         name='create'),
    path('etapas/<slug:slug>/apostar/',
         views.AdministrarApuestasFormView.as_view(),
         name='apostar'),
    path('etapas/<slug:slug>/editar/',
         views.EtapaUpdateView.as_view(),
         name='update'),
    path('etapas/<slug:slug>/cargar-resultados/',
         views.CargarResultadosView.as_view(),
         name='cargar_resultados'),
    path('etapas/<slug:slug>/',
         views.EtapaDetailView.as_view(),
         name='detail'),
]
