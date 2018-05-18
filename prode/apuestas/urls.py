from django.urls import path

from . import views

app_name = "apuestas"
urlpatterns = [
    path('etapas/<slug:slug>/editar/',
         views.AdministrarApuestasFormView.as_view(),
         name='editar'),
    path('etapas/<slug:slug>/',
         views.EtapaDetailView.as_view(),
         name='detail')
]
