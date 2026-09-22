from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio_sesion, name='login'),  # página principal
    path('registrarse/', views.registrar_usuario, name='registrar'),
    path('cerrar/', views.cerrar_sesion, name='cerrar_sesion'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path('seguidores/', views.seguidores, name='seguidores'),
    path('seguidores/<str:username>/', views.seguidores, name='seguidores_usuario'),
    path('perfil/<str:username>/', views.perfil_usuario, name='perfil_usuario'),
    path('perfil/seguir/<int:turista_id>/', views.toggle_seguir, name='toggle_seguir'),

]
