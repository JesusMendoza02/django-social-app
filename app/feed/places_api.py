import requests
from django.conf import settings


def categorizar_lugar(tipos):
    """
    Determina la categoría basándose en los tipos de Google Places
    """
    mapeo_categorias = {
        'restaurant': 'restaurante',
        'food': 'restaurante',
        'bar': 'bar',
        'night_club': 'bar',
        'cafe': 'cafe',
        'museum': 'museo',
        'art_gallery': 'museo',
        'park': 'parque',
        'tourist_attraction': 'monumento',
        'point_of_interest': 'monumento',
        'lodging': 'hotel',
        'church': 'iglesia',  # ← AGREGADO
        'place_of_worship': 'iglesia',  # ← AGREGADO
        'shopping_mall': 'centro_comercial',
        'store': 'tienda',
        'movie_theater': 'entretenimiento',
        'amusement_park': 'entretenimiento',
        'natural_feature': 'Formación natural',
    }
    
    for tipo in tipos:
        if tipo in mapeo_categorias:
            return mapeo_categorias[tipo]
    
    return 'otro'