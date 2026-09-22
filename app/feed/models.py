from django.db import models
from usuarios.models import Turista
from django.utils import timezone

class LugarTuristico(models.Model):
    CATEGORIAS = [
        ('restaurante', 'Restaurante'),
        ('bar', 'Bar'),
        ('cafe', 'Café'),
        ('museo', 'Museo'),
        ('parque', 'Parque'),
        ('monumento', 'Monumento'),
        ('iglesia', 'Iglesia'), 
        ('hotel', 'Hotel'),
        ('centro_comercial', 'Centro Comercial'),  
        ('tienda', 'Tienda'),  
        ('entretenimiento', 'Entretenimiento'),  
        ('otro', 'Otro'),
    ]
    
    nombre = models.CharField(max_length=200)
    ubicacion = models.CharField(max_length=250)
    categoria = models.CharField(max_length=50, choices=CATEGORIAS, default='otro')
    latitud = models.FloatField(null=True, blank=True)
    longitud = models.FloatField(null=True, blank=True)
    place_id = models.CharField(max_length=200, unique=True, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name_plural = "Lugares Turísticos"

class Resena(models.Model):
    lugar_turistico = models.ForeignKey(
        LugarTuristico,
        on_delete=models.CASCADE,
        related_name='resenas'
    )
    descripcion = models.TextField()
    fecha_visita = models.DateTimeField()
    calificacion = models.PositiveSmallIntegerField() 

    def __str__(self):
        return f"Reseña de {self.lugar_turistico} ({self.calificacion}/5)"

class Publicacion(models.Model):
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    reaccion = models.IntegerField(default=0)  
    turista = models.ForeignKey(
        Turista,
        on_delete=models.CASCADE,
        related_name='publicaciones'
    )
    resena = models.ForeignKey(
        Resena,
        on_delete=models.CASCADE,
        related_name='publicaciones'
    )

    def __str__(self):
        return f"Publicación de {self.turista} ({self.resena.lugar_turistico})"
    
    @property
    def total_likes(self):
        return self.likes.count()



class Fotografia(models.Model):
    resena = models.ForeignKey(
        Resena,
        on_delete=models.CASCADE,
        related_name='fotografias'
    )
    fotografia = models.ImageField(upload_to='fotos_resenas/')

    def __str__(self):
        return f"Foto de la reseña {self.resena.id}"
    

class Like(models.Model):
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE, related_name='likes')
    turista = models.ForeignKey(Turista, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('publicacion', 'turista')  # Evita likes duplicados

    def __str__(self):
        return f"{self.turista} dio like a {self.publicacion}"
    

class Comentario(models.Model):
    publicacion = models.ForeignKey(
        Publicacion,
        on_delete=models.CASCADE,
        related_name='comentarios'
    )
    turista = models.ForeignKey(
        Turista,
        on_delete=models.CASCADE,
        related_name='comentarios'
    )
    texto = models.TextField(max_length=500)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comentario de {self.turista} en {self.publicacion}"
    
class Notificacion(models.Model):
    TIPOS = [
        ('like', 'Like en tu publicación'),
        ('comentario', 'Comentario en tu publicación'),
        ('nueva_publicacion', 'Nueva publicación de alguien que sigues'),
        ('nuevo_seguidor', 'Nuevo seguidor'),
    ]

    receptor = models.ForeignKey(
        Turista,
        on_delete=models.CASCADE,
        related_name='notificaciones'
    )
    emisor = models.ForeignKey(
        Turista,
        on_delete=models.CASCADE,
        related_name='notificaciones_enviadas'
    )
    tipo = models.CharField(max_length=20, choices=TIPOS)
    publicacion = models.ForeignKey(
        Publicacion,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    fecha = models.DateTimeField(default=timezone.now)

    perfil_usuario = models.ForeignKey(
        Turista,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notificaciones_perfil'
    )

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.receptor} - {self.tipo}"
