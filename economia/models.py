from django.db import models
from django.contrib.auth.models import AbstractUser


# 🔹 A. BLOQUE DE USUARIOS Y PERFILES
class Usuario(AbstractUser):
    TIPO_USUARIO = [
        ('ahorrista', 'Ahorrista'),
        ('empresario', 'Empresario'),
        ('estudiante', 'Estudiante'),
        ('otro', 'Otro'),
    ]

    NIVEL_EDUCACION = [
        ('basico', 'Básico'),
        ('intermedio', 'Intermedio'),
        ('avanzado', 'Avanzado'),
    ]

    tipo_usuario = models.CharField(max_length=20, choices=TIPO_USUARIO, default='otro')
    nivel_educacion_financiera = models.CharField(max_length=20, choices=NIVEL_EDUCACION, default='basico')
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.tipo_usuario})"


# 🔹 B. BLOQUE DE FINANZAS PERSONALES

class Categoria(models.Model):
    TIPO_CATEGORIA = [
        ('ingreso', 'Ingreso'),
        ('gasto', 'Gasto'),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='categorias')
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=TIPO_CATEGORIA)

    class Meta:
        unique_together = ('usuario', 'nombre', 'tipo')

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"


class Ingreso(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='ingresos')
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    #fuente = models.CharField(max_length=100)
    fuente=models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name='ingresos')
    fecha = models.DateField()
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Ingreso {self.monto} - {self.fuente}"


class Gasto(models.Model):
    TIPO_PAGO = [
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia'),
        ('otro', 'Otro'),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='gastos')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name='gastos')
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateField()
    descripcion = models.TextField(blank=True, null=True)
    tipo_pago = models.CharField(max_length=20, choices=TIPO_PAGO)

    def __str__(self):
        return f"Gasto {self.monto} - {self.categoria}"


class MetaAhorro(models.Model):
    ESTADO_META = [
        ('progreso', 'En progreso'),
        ('cumplida', 'Cumplida'),
        ('vencida', 'Vencida'),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='metas')
    nombre_meta = models.CharField(max_length=100)
    monto_objetivo = models.DecimalField(max_digits=12, decimal_places=2)
    monto_actual = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fecha_inicio = models.DateField()
    fecha_limite = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADO_META, default='progreso')

    def progreso(self):
        return (self.monto_actual / self.monto_objetivo) * 100 if self.monto_objetivo > 0 else 0

    def __str__(self):
        return f"{self.nombre_meta} ({self.estado})"


class Alerta(models.Model):
    ESTADO_ALERTA = [
        ('activa', 'Activa'),
        ('atendida', 'Atendida'),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='alertas')
    tipo_alerta = models.CharField(max_length=100)
    mensaje = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_ALERTA, default='activa')

    def __str__(self):
        return f"Alerta: {self.tipo_alerta} ({self.estado})"


class Reporte(models.Model):
    TIPO_REPORTE = [
        ('mensual', 'Mensual'),
        ('anual', 'Anual'),
        ('personalizado', 'Personalizado'),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='reportes')
    tipo_reporte = models.CharField(max_length=20, choices=TIPO_REPORTE)
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    contenido_json = models.JSONField()

    def __str__(self):
        return f"Reporte {self.tipo_reporte} - {self.fecha_generacion.date()}"
