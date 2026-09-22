from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Like, Comentario, Publicacion, Notificacion
from usuarios.models import Seguidor

# Notificación por like
@receiver(post_save, sender=Like)
def crear_notificacion_like(sender, instance, created, **kwargs):
    if created and instance.publicacion.turista != instance.turista:
        Notificacion.objects.create(
            receptor=instance.publicacion.turista,
            emisor=instance.turista,
            tipo='like',
            publicacion=instance.publicacion,
            mensaje=f"{instance.turista} le dio like a tu publicación."
        )

# Notificación por comentario
@receiver(post_save, sender=Comentario)
def crear_notificacion_comentario(sender, instance, created, **kwargs):
    if created and instance.publicacion.turista != instance.turista:
        Notificacion.objects.create(
            receptor=instance.publicacion.turista,
            emisor=instance.turista,
            tipo='comentario',
            publicacion=instance.publicacion,
            mensaje=f"{instance.turista} comentó en tu publicación."
        )

# Notificación por nueva publicación
@receiver(post_save, sender=Publicacion)
def crear_notificacion_publicacion(sender, instance, created, **kwargs):
    if created:
        seguidores = instance.turista.seguidores.all()
        for seguidor in seguidores:
            Notificacion.objects.create(
                receptor=seguidor.turista_seguidor,
                emisor=instance.turista,
                tipo='nueva_publicacion',
                publicacion=instance,
                mensaje=f"{instance.turista} ha publicado algo nuevo."
            )

# Notificación por nuevo seguidor
@receiver(post_save, sender=Seguidor)
def crear_notificacion_seguidor(sender, instance, created, **kwargs):
    if created:
        Notificacion.objects.create(
            receptor=instance.turista_seguido,
            emisor=instance.turista_seguidor,
            tipo='nuevo_seguidor',
            mensaje=f"{instance.turista_seguidor} comenzó a seguirte.",
            perfil_usuario=instance.turista_seguidor
        )
