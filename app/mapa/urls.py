from django.urls import path
from . import views

app_name = "mapa"

urlpatterns = [
    path('<int:lugar_id>/', views.mapa_view, name='mapa'),
]