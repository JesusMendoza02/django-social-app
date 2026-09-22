from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.timesince import timesince
from django.urls import reverse
from datetime import datetime
from .forms import FormResena
from .models import Fotografia, Publicacion, Like, Comentario, LugarTuristico, Notificacion
from usuarios.models import Seguidor
from django.views.decorators.http import require_POST, require_http_methods
from django.http import JsonResponse
from .places_api import  categorizar_lugar
import requests
from django.conf import settings
import json
import traceback

@login_required
def buscar_lugares(request):
    import requests
    from django.http import JsonResponse
    from django.conf import settings

    query = request.GET.get("q", "").strip()
    if not query:
        return JsonResponse({"lugares": []})

    api_key = settings.GOOGLE_MAPS_API_KEY

    # Centro de Zacatecas
    lat = 22.7740
    lng = -102.5720
    radio = 25000  # 25 km

    # VERSION MAS SIMPLE Y COMPATIBLE
    url = (
        "https://maps.googleapis.com/maps/api/place/textsearch/json"
        f"?query={query}+zacatecas"
        f"&location={lat},{lng}"
        f"&radius={radio}"
        f"&language=es"
        f"&key={api_key}"
    )

    print("\n\nURL USADA PARA GOOGLE:\n", url, "\n\n")  # 🔥 IMPORTANTE PARA DEBUG

    response = requests.get(url)
    data = response.json()

    resultados_api = []

    for lugar in data.get("results", []):
        resultados_api.append({
            "id": None,
            "nombre": lugar.get("name"),
            "ubicacion": lugar.get("formatted_address", ""),
            "place_id": lugar.get("place_id"),
            "latitud": lugar["geometry"]["location"]["lat"],
            "longitud": lugar["geometry"]["location"]["lng"],
            "tipos": lugar.get("types", []),
        })

    return JsonResponse({"lugares": resultados_api})






@login_required
def publicar_resena(request):
    if request.method == 'POST':
        form_resena = FormResena(request.POST, request.FILES)
        fotos = request.FILES.getlist('fotografias')

        # === Validar cantidad de fotos ===
        if len(fotos) > 3:
            messages.error(request, "Solo puedes subir un máximo de 3 fotografías.")
            return render(request, 'publicacion_form.html', {
                'form_resena': form_resena,
                'username': request.user.username
            })

        try:
            # === MANEJAR LUGAR TURÍSTICO ===
            lugar_id = request.POST.get('lugar_turistico')
            lugar_turistico = None

            if lugar_id:
                # Lugar existente en la base de datos
                lugar_turistico = LugarTuristico.objects.get(id=lugar_id)
            else:
                # Crear nuevo lugar desde la API de Google
                nuevo_nombre = request.POST.get('nuevo_lugar_nombre')
                nuevo_ubicacion = request.POST.get('nuevo_lugar_ubicacion')
                nuevo_place_id = request.POST.get('nuevo_lugar_place_id')
                nuevo_lat = request.POST.get('nuevo_lugar_latitud')
                nuevo_lng = request.POST.get('nuevo_lugar_longitud')
                nuevo_tipos = request.POST.get('nuevo_lugar_tipos', '[]')

                if nuevo_nombre and nuevo_ubicacion:
                    if nuevo_place_id:
                        lugar_turistico, created = LugarTuristico.objects.get_or_create(
                            place_id=nuevo_place_id,
                            defaults={
                                'nombre': nuevo_nombre,
                                'ubicacion': nuevo_ubicacion,
                                'latitud': float(nuevo_lat) if nuevo_lat else None,
                                'longitud': float(nuevo_lng) if nuevo_lng else None,
                                'categoria': categorizar_lugar(json.loads(nuevo_tipos))
                            }
                        )
                    else:
                        # Crear sin place_id
                        lugar_turistico = LugarTuristico.objects.create(
                            nombre=nuevo_nombre,
                            ubicacion=nuevo_ubicacion,
                            latitud=float(nuevo_lat) if nuevo_lat else None,
                            longitud=float(nuevo_lng) if nuevo_lng else None,
                            categoria='otro'
                        )
                else:
                    messages.error(request, "Debes seleccionar un lugar válido antes de publicar.")
                    return render(request, 'publicacion_form.html', {
                        'form_resena': form_resena,
                        'username': request.user.username
                    })

            # === VALIDAR FORMULARIO ===
            if not form_resena.is_valid():
                messages.error(request, "Por favor completa todos los campos requeridos.")
                return render(request, 'publicacion_form.html', {
                    'form_resena': form_resena,
                    'username': request.user.username
                })

            # === CREAR RESEÑA ===
            resena = form_resena.save(commit=False)
            resena.lugar_turistico = lugar_turistico

            # Determinar fecha de visita
            actualmente = form_resena.cleaned_data.get('actualmente_en_lugar')
            if actualmente == 'si':
                resena.fecha_visita = timezone.now()
            else:
                fecha_manual = form_resena.cleaned_data.get('fecha_visita_manual')
                if fecha_manual:
                    if timezone.is_naive(fecha_manual):
                        resena.fecha_visita = timezone.make_aware(fecha_manual)
                    else:
                        resena.fecha_visita = fecha_manual
                else:
                    resena.fecha_visita = timezone.now()

            resena.save()

            # === GUARDAR FOTOS ===
            for foto in fotos:
                Fotografia.objects.create(resena=resena, fotografia=foto)

            # === CREAR PUBLICACIÓN ===
            Publicacion.objects.create(
                turista=request.user.datos,
                resena=resena
            )

            messages.success(request, "¡Reseña publicada con éxito!")
            return redirect('inicio:inicio')

        except Exception as e:
            print("Error completo:", e)
            traceback.print_exc()
            messages.error(request, f"Error al publicar la reseña: {str(e)}")

    else:
        form_resena = FormResena()

    return render(request, 'publicacion_form.html', {
        'form_resena': form_resena,
        'username': request.user.username
    })

@login_required
def eliminar_publicacion(request, publicacion_id):
    publicacion = get_object_or_404(Publicacion, id=publicacion_id)

    if publicacion.turista.usuario != request.user:
        messages.error(request, "No tienes permiso para eliminar esta publicación.")
        return redirect('perfil_usuario',request.user.username)

    if request.method == 'POST':
        publicacion.delete()
        messages.success(request, "Publicación eliminada con éxito.")
        return redirect('perfil_usuario',request.user.username) 

    return redirect('perfil_usuario',request.user.username)

@login_required
def visualizar_feed(request):
    categoria = request.GET.get('categoria', '')

    # Publicaciones ordenadas por fecha descendente
    publicaciones = (
        Publicacion.objects
        .select_related('turista', 'resena__lugar_turistico')
        .prefetch_related('resena__fotografias', 'comentarios')
    )

    username = request.user.username

    # Obtener los IDs de los usuarios que el actual sigue
    siguiendo_ids = Seguidor.objects.filter(
        turista_seguidor=request.user.datos
    ).values_list('turista_seguido_id', flat=True)

    # --- FILTRO POR CATEGORÍA ---
    if categoria:
        publicaciones = publicaciones.filter(resena__lugar_turistico__categoria=categoria)

    # --- ORDEN PERSONALIZADO ---
    # Primero las publicaciones de seguidos, luego las demás
    publicaciones = sorted(
        publicaciones,
        key=lambda pub: (
            0 if pub.turista_id in siguiendo_ids else 1,  # Prioridad: seguidos primero
            -pub.fecha_publicacion.timestamp()             # Dentro del grupo, más recientes primero
        )
    )

    # Categorías únicas para el filtro
    categorias = LugarTuristico.objects.values_list('categoria', flat=True).distinct()

    # Likes del usuario actual
    likes_usuario = set()
    if request.user.is_authenticated and hasattr(request.user, 'datos'):
        likes_usuario = set(
            Like.objects.filter(turista=request.user.datos)
            .values_list('publicacion_id', flat=True)
        )

    context = {
        'publicaciones': publicaciones,
        'likes_usuario': likes_usuario,
        'categorias': categorias,
        'categoria_actual': categoria,
        'username': username,
    }

    return render(request, 'feed.html', context)

@login_required
@require_POST
def dar_like(request, publicacion_id):
    publicacion = get_object_or_404(Publicacion, id=publicacion_id)
    turista = request.user.datos

    if publicacion.turista == turista:
        return JsonResponse({'error': 'No puedes dar like a tu propia publicación.'}, status=400)

    # --- Toggle del like ---
    like, creado = Like.objects.get_or_create(publicacion=publicacion, turista=turista)

    if not creado:
        # Se quitó el like → eliminar notificación existente
        Notificacion.objects.filter(
            tipo='like',
            emisor=turista,
            receptor=publicacion.turista,
            publicacion=publicacion
        ).delete()

        like.delete()
        liked = False
    else:
        liked = True

        # Solo crear notificación si NO existe
        Notificacion.objects.get_or_create(
            tipo='like',
            emisor=turista,
            receptor=publicacion.turista,
            publicacion=publicacion,
            defaults={
                'mensaje': f"{turista.usuario.username} le dio like a tu publicación."
            }
        )

    # Actualizar contador
    publicacion.reaccion = publicacion.likes.count()
    publicacion.save(update_fields=['reaccion'])

    return JsonResponse({
        'liked': liked,
        'total_likes': publicacion.reaccion
    })




@login_required
def escribir_comentario(request, publicacion_id=None):
    if not publicacion_id:
        return redirect('inicio:inicio')  # Redirige al feed si no hay ID

    publicacion = get_object_or_404(Publicacion, id=publicacion_id)
    texto = request.POST.get('texto', '').strip()

    if not texto:
        return redirect('inicio:detalle_publicacion', publicacion_id=publicacion.id)

    if len(texto) > 150:
        return redirect('inicio:detalle_publicacion', publicacion_id=publicacion.id)

    Comentario.objects.create(
        publicacion=publicacion,
        turista=request.user.datos,
        texto=texto
    )
    return redirect('inicio:detalle_publicacion', publicacion_id=publicacion.id)


@login_required
def eliminar_comentario(request, comentario_id=None):
    if not comentario_id:
        return redirect('inicio:inicio')  # Redirige al feed si no hay ID

    comentario = get_object_or_404(Comentario, id=comentario_id)

    # Verificar que el usuario actual sea el autor del comentario
    if comentario.turista.usuario != request.user:
        return redirect('inicio:detalle_publicacion', publicacion_id=comentario.publicacion.id)

    if request.method == 'POST':
        publicacion_id = comentario.publicacion.id  # Guardamos ID antes de borrar
        comentario.delete()
        return redirect('inicio:detalle_publicacion', publicacion_id=publicacion_id)

    # Opcional: si deseas mostrar una confirmación antes de eliminar
    return render(request, 'confirmar_eliminar_comentario.html', {'comentario': comentario})


@login_required
def detalle_publicacion(request, publicacion_id):
    publicacion = get_object_or_404(
        Publicacion.objects
        .select_related('turista', 'resena__lugar_turistico')
        .prefetch_related('resena__fotografias', 'comentarios__turista__usuario'),
        id=publicacion_id
    )

    likes_usuario = set()
    if hasattr(request.user, 'datos'):
        likes_usuario = set(Like.objects.filter(turista=request.user.datos)
                            .values_list('publicacion_id', flat=True))

    context = {
        'publicacion': publicacion,
        'usuario': request.user,
        'username': request.user.username,
        'likes_usuario': likes_usuario
    }
    return render(request, 'detalle_publicacion.html', context)

@login_required
def obtener_notificaciones(request):
    """
    Obtiene únicamente las notificaciones NO LEÍDAS del usuario.
    Cada una contiene su ícono, mensaje, tiempo y URL.
    """
    qs = Notificacion.objects.filter(
        receptor=request.user.datos,
        leida=False  # 🔹 Solo las no leídas
    ).order_by('-fecha')[:10]

    data = []
    for n in qs:
        
        url = "#" 

        # Ícono según tipo
        if n.tipo == 'like':
            icono = 'bi-hand-thumbs-up-fill text-primary'
        elif n.tipo == 'comentario':
            icono = 'bi-chat-dots-fill text-success'
        elif n.tipo == 'nuevo_seguidor':
            icono = 'bi-person-plus-fill text-warning'
        elif n.tipo == 'nueva_publicacion':
            icono = 'bi-bell-fill text-info'
        else:
            icono = 'bi-bell'

        texto = n.mensaje or "Tienes una nueva notificación"

        data.append({
            'id': n.id,
            'mensaje': texto,
            'texto': texto,  # compatibilidad para feed
            'fecha': n.fecha.strftime('%d/%m/%Y %H:%M'),
            'tiempo': timesince(n.fecha) + " atrás",
            'leida': n.leida,
            'url': url,
            'icono': icono,
        })

    nuevas = qs.count()  # 🔹 Solo cuenta las no leídas

    return JsonResponse({'notificaciones': data, 'nuevas': nuevas})


@login_required
def limpiar_notificaciones(request):
    Notificacion.objects.filter(
        receptor=request.user.datos,
        leida=False
    ).delete()

    return JsonResponse({'status': 'ok'})
