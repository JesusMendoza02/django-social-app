from django.urls import path
from . import views

app_name = 'feed'

urlpatterns = [
    path('', views.visualizar_feed, name='inicio'),
    path('buscar-lugares/', views.buscar_lugares, name='buscar_lugares'),
    path('publicar/', views.publicar_resena, name='publicar'), 
    path('feed/', views.visualizar_feed, name='feed'),
    path('like/<int:publicacion_id>/', views.dar_like, name='dar_like'),
    path('eliminar/<int:publicacion_id>/', views.eliminar_publicacion, name='eliminar_publicacion'),
    path('comentario/<int:publicacion_id>/', views.escribir_comentario, name='escribir_comentario'),
    path('comentario/eliminar/<int:comentario_id>/', views.eliminar_comentario, name='eliminar_comentario'),
    path('publicacion/<int:publicacion_id>/', views.detalle_publicacion, name='detalle_publicacion'),
    path('notificaciones/', views.obtener_notificaciones, name='obtener_notificaciones'),
    path('publicacion/<int:pk>/', views.detalle_publicacion, name='detalle_publicacion'),
    path('notificaciones/limpiar/', views.limpiar_notificaciones, name='limpiar_notificaciones'),

]