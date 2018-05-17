from django.urls import path

from . import views

app_name = "apuestas"
urlpatterns = [
    path('<slug:slug>/editar/', views.AdministrarApuestasFormView.as_view(), name='editar')
]
