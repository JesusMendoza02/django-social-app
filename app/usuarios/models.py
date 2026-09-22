from django.db import models
from django.contrib.auth.models import User

class Turista(models.Model):
    usuario = models.OneToOneField(User, verbose_name="Usuario",related_name='datos', on_delete=models.CASCADE)
    foto_perfil = models.ImageField(upload_to='fotos_perfil/', blank=True,null=True)
    biografia = models.TextField(blank=True)
    fecha_nac = models.DateField()
    def __str__(self):
        return self.usuario.username
    


class Seguidor(models.Model):
    turista_seguidor = models.ForeignKey(
        Turista,
        related_name='siguiendo',
        on_delete=models.CASCADE
    )
    turista_seguido = models.ForeignKey(
        Turista,
        related_name='seguidores',
        on_delete=models.CASCADE
    )
    fecha_seguimiento = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('turista_seguidor', 'turista_seguido')



