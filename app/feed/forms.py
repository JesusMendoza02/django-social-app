from django import forms
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
from .models import Resena


# ---------- WIDGETS PERSONALIZADOS ----------
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        # Adaptar para listas de archivos múltiples
        single_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_clean(d, initial) for d in data]
        return single_clean(data, initial)


# ---------- FORMULARIO PRINCIPAL ----------
class FormResena(forms.ModelForm):

    fotografias = MultipleFileField(
        required=False,
        label='Fotografías (máximo 3)',
        widget=MultipleFileInput(attrs={
            'accept': 'image/*',
            'class': 'form-control',
        })
    )

    actualmente_en_lugar = forms.ChoiceField(
        choices=[('si', 'Sí'), ('no', 'No')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='si',
        label='¿Actualmente en el lugar?'
    )

    fecha_visita_manual = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        }),
        label='Fecha y hora de visita',
        help_text='Debe ser dentro del último mes y no puede ser futura.'
    )

    class Meta:
        model = Resena
        # ⚠️ Quitamos 'lugar_turistico' porque se maneja manualmente en la vista
        fields = ['descripcion', 'calificacion']

        widgets = {
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Escribe tu experiencia...'
            }),
            'calificacion': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10,
                'placeholder': '1 a 10'
            }),
        }

        labels = {
            'descripcion': 'Descripción de la visita',
            'calificacion': 'Calificación (1-10)',
        }

    # ---------- VALIDACIONES ----------
    def clean_calificacion(self):
        calificacion = self.cleaned_data.get('calificacion')
        if calificacion is not None and (calificacion < 1 or calificacion > 10):
            raise ValidationError("La calificación debe estar entre 1 y 10.")
        return calificacion

    def clean_fecha_visita_manual(self):
        fecha_manual = self.cleaned_data.get('fecha_visita_manual')

        if fecha_manual:
            ahora = timezone.now()
            if timezone.is_naive(fecha_manual):
                fecha_manual = timezone.make_aware(fecha_manual)

            if fecha_manual > ahora:
                raise ValidationError("No puedes seleccionar una fecha futura.")
            if fecha_manual < (ahora - timedelta(days=30)):
                raise ValidationError("La fecha de visita debe ser dentro del último mes.")
        return fecha_manual

    def clean_fotografias(self):
        fotos = self.cleaned_data.get('fotografias')

        if not fotos:
            return fotos

        if len(fotos) > 3:
            raise ValidationError("Solo puedes subir un máximo de 3 fotografías.")

        formatos_validos = ['image/jpeg', 'image/png', 'image/webp']
        for foto in fotos:
            if foto.content_type not in formatos_validos:
                raise ValidationError(
                    f"El archivo '{foto.name}' no es válido. Solo se permiten JPG, PNG o WEBP."
                )
        return fotos

    def clean(self):
        cleaned_data = super().clean()
        actualmente = cleaned_data.get('actualmente_en_lugar')
        fecha_manual = cleaned_data.get('fecha_visita_manual')

        if actualmente == 'no' and not fecha_manual:
            self.add_error('fecha_visita_manual', 'Debes indicar la fecha y hora de tu visita.')
        return cleaned_data
