from django import forms
from .models import Usuario, Ingreso, Gasto, Categoria, MetaAhorro, Alerta
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

#🧩 2. Formularios de usuario
#🔹 Registro de usuario
class UsuarioRegistroForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'tipo_usuario', 'nivel_educacion_financiera', 'password1', 'password2'
        ]
        widgets = {
            'tipo_usuario': forms.Select(attrs={'class': 'form-control'}),
            'nivel_educacion_financiera': forms.Select(attrs={'class': 'form-control'}),
        }


class UsuarioUpdateForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'tipo_usuario', 'nivel_educacion_financiera']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

#🧩 3. Formularios financieros
#🔹 Categoría

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'tipo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Alimentación'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
        }

#🔹 Ingreso

class IngresoForm(forms.ModelForm):
    class Meta:
        model = Ingreso
        fields = ['monto', 'fuente', 'fecha', 'descripcion']
        widgets = {
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'fuente':forms.Select(attrs={'class': 'form-select'}),
            #'fuente': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('usuario', None)  # <-- recibimos el usuario desde la vista
        super().__init__(*args, **kwargs)
        if usuario:
            self.fields['fuente'].queryset = Categoria.objects.filter(usuario=usuario, tipo='ingreso')

#🔹 Gasto
class GastoForm(forms.ModelForm):
    class Meta:
        model = Gasto
        fields = ['categoria', 'monto', 'fecha', 'descripcion', 'tipo_pago']
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'tipo_pago': forms.Select(attrs={'class': 'form-select'}),
        }
        
    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        if usuario:
            self.fields['categoria'].queryset = Categoria.objects.filter(usuario=usuario, tipo='gasto')

#🔹 Meta de Ahorro
class MetaAhorroForm(forms.ModelForm):
    class Meta:
        model = MetaAhorro
        fields = ['nombre_meta', 'monto_objetivo', 'monto_actual', 'fecha_inicio', 'fecha_limite', 'estado']
        widgets = {
            'nombre_meta': forms.TextInput(attrs={'class': 'form-control'}),
            'monto_objetivo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'monto_actual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_limite': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)

    def clean_monto_actual(self):
        monto_actual = self.cleaned_data.get('monto_actual', 0)

        # Solo validamos si hay usuario
        if self.usuario:
            from django.db.models import Sum
            from economia.models import Ingreso, Gasto, MetaAhorro

            # Calcular saldo actual del usuario
            total_ingresos = Ingreso.objects.filter(usuario=self.usuario).aggregate(Sum('monto'))['monto__sum'] or 0
            total_gastos = Gasto.objects.filter(usuario=self.usuario).aggregate(Sum('monto'))['monto__sum'] or 0
            saldo_actual = total_ingresos - total_gastos

            # Calcular cuánto ya está comprometido en otras metas
            metas_existentes = MetaAhorro.objects.filter(usuario=self.usuario).exclude(pk=self.instance.pk)
            total_asignado = metas_existentes.aggregate(Sum('monto_actual'))['monto_actual__sum'] or 0

            # Calcular saldo disponible
            saldo_disponible = saldo_actual - total_asignado

            # Validar el monto ingresado
            if monto_actual > saldo_disponible:
                # Sobrescribir el valor y mostrar advertencia
                self.cleaned_data['monto_actual'] = saldo_disponible
                raise ValidationError(
                    f"El monto ingresado supera tu saldo disponible. Tu saldo maximio es Bs. {saldo_disponible:.2f}"
                )

        return monto_actual

#🔹 Alerta (generalmente automática, pero editable si se desea)
class AlertaForm(forms.ModelForm):
    class Meta:
        model = Alerta
        fields = ['tipo_alerta', 'mensaje', 'estado']
        widgets = {
            'tipo_alerta': forms.TextInput(attrs={'class': 'form-control'}),
            'mensaje': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }
