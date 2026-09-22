from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Turista
from datetime import date

class FormUser(forms.ModelForm):
    re_pass = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control auth-input',
            'placeholder': 'Confirma tu contraseña'
        }),
        required=True
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control auth-input',
            'placeholder': 'Mínimo 8 caracteres'
        }),
        required=True
    )
    username = forms.CharField(
        label='Nombre de usuario',
        widget=forms.TextInput(attrs={
            'class': 'form-control auth-input',
            'placeholder': 'Elige un nombre de usuario'
        })
    )
    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control auth-input',
            'placeholder': 'Escribe tu correo'
        }),
        required=True
    )
    first_name = forms.CharField(
        label='Nombre',
        widget=forms.TextInput(attrs={
            'class': 'form-control auth-input',
            'placeholder': 'Escribe tu nombre'
        }),
        required=True
    )
    last_name = forms.CharField(
        label='Apellidos',
        widget=forms.TextInput(attrs={
            'class': 'form-control auth-input',
            'placeholder': 'Escribe tus apellidos'
        }),
        required=True
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 're_pass']

    def clean_password(self):
        password = self.data.get('password')
        re_pass = self.data.get('re_pass')
        if password != re_pass:
            raise forms.ValidationError('Las contraseñas no coinciden')
        if len(password) < 8:
            raise forms.ValidationError('La contraseña debe tener al menos 8 caracteres')
        return password

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Este nombre de usuario ya existe')
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class FormTurista(forms.ModelForm):
    class Meta:
        model = Turista
        fields = ['fecha_nac']  
        widgets = {
            'fecha_nac': forms.DateInput(attrs={
                'class': 'form-control auth-input',
                'type': 'date',
                'placeholder': 'Selecciona tu fecha de nacimiento'
            }),
        }
        labels = {
            'fecha_nac': 'Fecha de nacimiento',
        }
        
    def clean_fecha_nac(self):
        from datetime import date
        fecha_nac = self.cleaned_data.get('fecha_nac')
        if fecha_nac:
            edad = (date.today() - fecha_nac).days // 365
            if edad < 13:
                raise forms.ValidationError('Debes tener al menos 13 años para registrarte')
        return fecha_nac
    
# Formulario para editar los campos del modelo User
class FormEdicionUser(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        labels = {
            'username': 'Nombre de usuario', 
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo Electrónico',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control auth-input'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control auth-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control auth-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-control auth-input'}),
        }
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Este nombre de usuario ya está en uso.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado por otro usuario.')
        return email


# Formulario para editar los campos del modelo Turista
class FormEdicionTurista(forms.ModelForm):
    # fecha_nac = forms.DateField(
    #     required=False, 
    #     widget=forms.DateInput(attrs={'class': 'form-control auth-input', 'type': 'date'}),
    #     label='Fecha de Nacimiento'
    # )

    class Meta:
        model = Turista
        fields = ['foto_perfil', 'biografia'] # 'fecha_nac'
        labels = {
            'foto_perfil': 'Foto de Perfil',
            'biografia': 'Biografía',
        }
        widgets = {
            'biografia': forms.Textarea(attrs={
                'class': 'form-control auth-input', 
                'rows': 4, 
                'style': 'min-height: 120px;', 
                'placeholder': 'Comparte algo sobre ti...'
            }),
            'foto_perfil': forms.FileInput(attrs={'id': 'id_foto_perfil', 'class': 'form-control'}),
        }

    # def clean_fecha_nac(self):
    #     fecha_nac = self.cleaned_data.get('fecha_nac')
    #     if fecha_nac:
    #         edad = (date.today() - fecha_nac).days // 365
    #         if edad < 13:
    #             raise forms.ValidationError('Debes tener al menos 13 años.')
    #     return fecha_nac


# Formulario para cambiar la contraseña
class FormCambiarContrasena(forms.Form):
    new_password = forms.CharField(
        label='Nueva Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control auth-input', 'placeholder': 'Dejar vacío para no cambiar'}),
        strip=False,
        required=False
    )
    confirm_password = forms.CharField(
        label='Confirmar Nueva Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control auth-input', 'placeholder': 'Dejar vacío para no cambiar'}),
        strip=False,
        required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password or confirm_password:
            if not new_password or not confirm_password:
                 self.add_error('confirm_password', 'Debes ingresar y confirmar la nueva contraseña.')
            elif new_password != confirm_password:
                self.add_error('confirm_password', 'Las contraseñas no coinciden.')
            elif len(new_password) < 8:
                self.add_error('new_password', 'La contraseña debe tener al menos 8 caracteres.')
        
        return cleaned_data