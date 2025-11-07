import json
from datetime import date
from decimal import Decimal
from django.db.models import Sum
from .models import Ingreso, Gasto, MetaAhorro, Reporte

def generar_reporte_mensual(usuario):
    """Genera un reporte mensual con ingresos, gastos y metas del usuario y lo guarda en Reporte."""
    hoy = date.today()
    mes_actual = hoy.month
    año_actual = hoy.year

    # Ingresos del mes
    ingresos_mes = Ingreso.objects.filter(
        usuario=usuario,
        fecha__month=mes_actual,
        fecha__year=año_actual
    )
    total_ingresos = ingresos_mes.aggregate(total=Sum('monto'))['total'] or Decimal('0.00')

    # Gastos del mes
    gastos_mes = Gasto.objects.filter(
        usuario=usuario,
        fecha__month=mes_actual,
        fecha__year=año_actual
    )
    total_gastos = gastos_mes.aggregate(total=Sum('monto'))['total'] or Decimal('0.00')

    # Metas de ahorro
    metas = MetaAhorro.objects.filter(usuario=usuario)
    metas_data = [
        {
            "nombre_meta": m.nombre_meta,
            "monto_objetivo": float(m.monto_objetivo),
            "monto_actual": float(m.monto_actual),
            'progreso': round(m.progreso(), 2),
            "estado": m.estado,
            "fecha_limite": m.fecha_limite.strftime("%d/%m/%Y"),
        }
        for m in metas
    ]

    # Saldo neto
    saldo_neto = total_ingresos - total_gastos

    # Contenido del reporte
    contenido = {
        "mes": hoy.strftime("%B %Y"),
        "resumen": {
            "total_ingresos": float(total_ingresos),
            "total_gastos": float(total_gastos),
            "saldo_neto": float(saldo_neto),
        },
        "detalle_ingresos": [
            {
                "fecha": i.fecha.strftime("%d/%m/%Y"),
                "monto": float(i.monto),
                "descripcion": i.descripcion or "",
            }
            for i in ingresos_mes
        ],
        "detalle_gastos": [
            {
                "fecha": g.fecha.strftime("%d/%m/%Y"),
                "monto": float(g.monto),
                "descripcion": g.descripcion or "",
            }
            for g in gastos_mes
        ],
        "metas_ahorro": metas_data,
    }

    # 🔒 Serializar de forma segura a JSON
    contenido_serializado = json.loads(json.dumps(contenido, default=str))

    # Guardar el reporte
    Reporte.objects.create(
        usuario=usuario,
        tipo_reporte='mensual',
        contenido_json=contenido_serializado
    )

    return contenido_serializado
