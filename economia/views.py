from django.shortcuts import render

# Create your views here.
# economia/views.py

from django.db.models.functions import ExtractMonth
from django.views.generic import DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, ListView
from .models import Ingreso
from .forms import IngresoForm , MetaAhorroForm
from django.contrib import messages

class IngresoCreateView(LoginRequiredMixin, CreateView):
#class IngresoCreateView( CreateView):
    model = Ingreso
    form_class = IngresoForm
    
    template_name = 'economia/ingresos_form.html'
    success_url = reverse_lazy('ingreso_nuevo')


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['usuario'] = self.request.user  # 👈 pasamos el usuario al formulario
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categorias"] = Categoria.objects.filter(usuario=self.request.user)
        return context

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(self.request, "Ingreso registrado correctamente 🎉")
        return super().form_valid(form)

class IngresoUpdateView(LoginRequiredMixin, UpdateView):
    model = Ingreso
    form_class = IngresoForm
    template_name = 'economia/ingresos_form.html'
    success_url = reverse_lazy('ingreso_nuevo')

class IngresoDeleteView(LoginRequiredMixin, DeleteView):
    model = Ingreso
    template_name = 'economia/ingreso_confirmar_eliminar.html'
    success_url = reverse_lazy('ingresos_lista')

    def get_queryset(self):
        # Asegura que solo se puedan eliminar los ingresos del usuario actual
        return Ingreso.objects.filter(usuario=self.request.user)
    

# economia/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Ingreso, Gasto, MetaAhorro
from django.db.models import Sum

@login_required
def dashboard(request):
    usuario = request.user

    total_ingresos = Ingreso.objects.filter(usuario=usuario).aggregate(Sum('monto'))['monto__sum'] or 0
    total_gastos = Gasto.objects.filter(usuario=usuario).aggregate(Sum('monto'))['monto__sum'] or 0
    saldo_actual = total_ingresos - total_gastos

    metas_cumplidas = MetaAhorro.objects.filter(usuario=usuario, estado='cumplida').count()

    ultimos_ingresos = Ingreso.objects.filter(usuario=usuario).order_by('-fecha')[:5]
    ultimos_gastos = Gasto.objects.filter(usuario=usuario).order_by('-fecha')[:5]
#
    movimientos_ingresos = [
        {'fecha': i.fecha, 'tipo': 'Ingreso', 'descripcion': i.descripcion, 'monto': i.monto}
        for i in ultimos_ingresos
    ]

    movimientos_gastos = [
        {'fecha': g.fecha, 'tipo': 'Gasto', 'descripcion': g.descripcion, 'monto': g.monto}
        for g in ultimos_gastos
    ]

    # Combinar y ordenar por fecha descendente
    ultimos_movimientos = sorted(
        movimientos_ingresos + movimientos_gastos,
        key=lambda x: x['fecha'],
        reverse=True
    )

    # datos para gráficos
    labels_gastos = list(Gasto.objects.filter(usuario=usuario)
                         .values_list('categoria__nombre', flat=True)
                         .distinct())
    data_gastos = [Gasto.objects.filter(usuario=usuario, categoria__nombre=cat)
                   .aggregate(Sum('monto'))['monto__sum'] for cat in labels_gastos]

    # ejemplo de ingresos mensuales
    labels_ingresos = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
    #data_ingresos = [0,0,0,0,0,0,0,0,0,0,0,0]  # luego puedes agregar lógica real

    # Obtener ingresos agrupados por mes
    ingresos_mensuales = (
        Ingreso.objects
        .filter(usuario=usuario)
        .annotate(mes=ExtractMonth('fecha'))
        .values('mes')
        .annotate(total=Sum('monto'))
        .order_by('mes')
    )

    # Crear lista de 12 posiciones (una por mes)
    data_ingresos = [0] * 12
    for item in ingresos_mensuales:
        mes = item['mes']
        if mes:
            data_ingresos[mes - 1] = float(item['total'])

    #Gastos
    gastos_mensuales = (
    Gasto.objects
    .filter(usuario=usuario)
    .annotate(mes=ExtractMonth('fecha'))
    .values('mes')
    .annotate(total=Sum('monto'))
    .order_by('mes')
)

    data_gastos_mensuales = [0] * 12
    for item in gastos_mensuales:
        mes = item['mes']
        if mes:
            data_gastos_mensuales[mes - 1] = float(item['total'])

    context = {
        'total_ingresos': total_ingresos,
        'total_gastos': total_gastos,
        'saldo_actual': saldo_actual,
        'metas_cumplidas': metas_cumplidas,
        'ultimos_movimientos': ultimos_movimientos,
        'labels_gastos': labels_gastos,
        'data_gastos': data_gastos_mensuales,
        'labels_ingresos': labels_ingresos,
        'data_ingresos': data_ingresos,
    }
    return render(request, 'economia/dashboard.html', context)


from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import Gasto

class GastoListView(LoginRequiredMixin, ListView):
    model = Gasto
    template_name = 'economia/gastos_list.html'
    context_object_name = 'gastos'

    def get_queryset(self):
        return Gasto.objects.filter(usuario=self.request.user).order_by('-fecha')


class IngresoListView(LoginRequiredMixin, ListView):
    model = Ingreso
    template_name = 'economia/ingresos_lista.html'
    context_object_name = 'ingresos'

    def get_queryset(self):
        return Ingreso.objects.filter(usuario=self.request.user).order_by('-fecha')



# economia/views.py
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from .forms import GastoForm

class GastoCreateView(LoginRequiredMixin, CreateView):
    model = Gasto
    form_class = GastoForm
    template_name = 'economia/gastos_form.html'
    success_url = reverse_lazy('gasto_nuevo')

    def get_form_kwargs(self):
            kwargs = super().get_form_kwargs()
            kwargs['usuario'] = self.request.user  # 👈 Pasamos el usuario al formulario
            return kwargs


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categorias"] = Categoria.objects.filter(usuario=self.request.user)
        return context
    
    def form_valid(self, form):
        form.instance.usuario = self.request.user        
        messages.success(self.request, "Gasto registrado correctamente 🎉")
        return super().form_valid(form)

class GastoUpdateView(LoginRequiredMixin, UpdateView):
    model = Gasto
    form_class = GastoForm
    template_name = 'economia/gastos_form.html'
    success_url = reverse_lazy('gastos_lista')

class GastoDeleteView(LoginRequiredMixin, DeleteView):
    model = Gasto
    template_name = 'economia/confirmar_eliminar.html'
    success_url = reverse_lazy('gastos_lista')


# Nuevo usuario

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from .forms import UsuarioRegistroForm

def registrar_usuario(request):
    if request.method == 'POST':
        form = UsuarioRegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)  # inicia sesión automáticamente tras registrarse
            messages.success(request, 'Tu cuenta ha sido creada exitosamente.')
            return redirect('ingreso_nuevo')  # cambia 'inicio' por la vista a la que quieras redirigir
    else:
        form = UsuarioRegistroForm()
    
    return render(request, 'economia/registro.html', {'form': form})


#Creaer categorias

from django.views.generic import CreateView
from django.urls import reverse_lazy
from .models import Categoria
from .forms import CategoriaForm

class CategoriaCreateView(CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'economia/categorias_form.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        # Asigna automáticamente el usuario autenticado
        form.instance.usuario = self.request.user
        return super().form_valid(form)
    
class CategoriaListView(LoginRequiredMixin, ListView):
    model = Categoria
    template_name = 'economia/categorias_lista.html'
    context_object_name = 'categorias'

    def get_queryset(self):
        return Categoria.objects.filter(usuario=self.request.user).order_by('nombre')
    
class CategoriaUpdateView(LoginRequiredMixin, UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'economia/categorias_form.html'
    success_url = reverse_lazy('categorias_lista')

    def get_queryset(self):
        return Categoria.objects.filter(usuario=self.request.user)
    
class CategoriaDeleteView(LoginRequiredMixin, DeleteView):
    model = Categoria
    template_name = 'economia/categoria_confirm_delete.html'
    success_url = reverse_lazy('categorias_lista')

    def get_queryset(self):
        return Categoria.objects.filter(usuario=self.request.user)
    

#Metas
class MetaAhorroListView(LoginRequiredMixin, ListView):
    model = MetaAhorro
    template_name = 'economia/metas_lista.html'
    context_object_name = 'metas'

    def get_queryset(self):
        return MetaAhorro.objects.filter(usuario=self.request.user)

class MetaAhorroCreateView(LoginRequiredMixin, CreateView):
    model = MetaAhorro
    form_class = MetaAhorroForm
    template_name = 'economia/meta_form.html'
    success_url = reverse_lazy('meta_nueva')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['usuario'] = self.request.user  # importante
        return kwargs

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(self.request, "Meta registrada correctamente 🎉")
        return super().form_valid(form)


class MetaAhorroUpdateView(LoginRequiredMixin, UpdateView):
    model = MetaAhorro
    form_class = MetaAhorroForm
    template_name = 'economia/meta_form.html'
    success_url = reverse_lazy('metas_lista')

class MetaAhorroDeleteView(LoginRequiredMixin, DeleteView):
    model = MetaAhorro
    template_name = 'economia/meta_confirm_delete.html'
    success_url = reverse_lazy('metas_lista')


#para generar el reporte 
from django.shortcuts import render, redirect
from django.contrib import messages
from .services import generar_reporte_mensual
from .models import Reporte

from django.shortcuts import render
from .models import Reporte

from django.contrib import messages
from django.shortcuts import redirect
from .services import generar_reporte_mensual

def reporte_generar(request):
    contenido = generar_reporte_mensual(request.user)

    # soporta ambas estructuras (por compatibilidad): 'resumen.saldo_neto' o 'balance'
    saldo = None
    if isinstance(contenido, dict):
        saldo = contenido.get('resumen', {}).get('saldo_neto')
        if saldo is None:
            # compatibilidad con versiones antiguas que devolvían 'balance'
            saldo = contenido.get('balance')

    saldo = float(saldo or 0)

    messages.success(request, f"✅ Reporte mensual generado correctamente. Balance: Bs {saldo:.2f}")
    return redirect('reportes_lista')



def reportes_lista(request):
    reportes = Reporte.objects.filter(usuario=request.user).order_by('-fecha_generacion')
    return render(request, 'economia/reportes_lista.html', {'reportes': reportes})


class ReporteEliminarView(LoginRequiredMixin, DeleteView):
    model = Reporte
    template_name = 'economia/confirmar_eliminar_reporte.html'
    success_url = reverse_lazy('reportes_lista')

    def get_queryset(self):
        # Solo permite eliminar los reportes del usuario actual
        return Reporte.objects.filter(usuario=self.request.user)
    
#Reporte PDF

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse
import json
from decimal import Decimal

from .models import Reporte

def reporte_pdf(request, reporte_id):
    reporte = Reporte.objects.get(id=reporte_id, usuario=request.user)

    # Crear respuesta HTTP con encabezado de PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_{reporte.id}.pdf"'

    # Crear documento PDF
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    p.setFont("Helvetica-Bold", 14)
    p.drawString(200, height - 50, "📊 Reporte Financiero")

    p.setFont("Helvetica", 10)
    p.drawString(50, height - 80, f"Tipo de reporte: {reporte.get_tipo_reporte_display()}")
    p.drawString(50, height - 100, f"Fecha de generación: {reporte.fecha_generacion.strftime('%d/%m/%Y %H:%M')}")

    # Contenido JSON
    y = height - 130
    p.setFont("Helvetica", 9)

    contenido = reporte.contenido_json

    def normalize(v):
        return str(v) if isinstance(v, Decimal) else v

    for clave, valor in contenido.items():
        # ✅ Si el valor es un diccionario, lo mostramos anidado
        if isinstance(valor, dict):
            p.drawString(50, y, f"{clave.capitalize()}:")
            y -= 15
            for subk, subv in valor.items():
                p.drawString(70, y, f"- {subk.replace('_', ' ').capitalize()}: {normalize(subv)}")
                y -= 12
            y -= 5

        # ✅ Si el valor es una lista (detalle_ingresos, metas, etc.)
        elif isinstance(valor, list):
            p.drawString(50, y, f"{clave.capitalize()}:")
            y -= 15
            for item in valor:
                for subk, subv in item.items():
                    p.drawString(70, y, f"- {subk.replace('_', ' ').capitalize()}: {normalize(subv)}")
                    y -= 12
                y -= 5

        # ✅ Si es un valor simple
        else:
            p.drawString(50, y, f"{clave.capitalize()}: {normalize(valor)}")
            y -= 15

        # Salto de página si hace falta
        if y < 80:
            p.showPage()
            y = height - 50
            p.setFont("Helvetica", 9)

    p.save()
    return response


#mport os,json
#mport requests
#rom django.conf import settings
#rom django.shortcuts import render
#
#ef chat_llama(request):
#   respuesta = None
#   
#   # Cargar tu archivo inflacion.json
#   ruta = os.path.join(settings.BASE_DIR, "economia", "inflacion.json")
#
#   with open(ruta, "r") as f:
#       datos = json.load(f)
#
#   contexto = f"Estos son los datos de inflación:\n{datos}\n"
#
#   if request.method == "POST":
#       pregunta = request.POST.get("pregunta")
#
#       payload = {
#            "model": "llama3:8b",
#            "prompt": contexto + "\nPregunta: " + pregunta,
#            "stream": False
#        }
#
#       r = requests.post("http://localhost:11434/api/generate", json=payload)
#       data = r.json()
#       respuesta = data.get("response", "")
#
#   return render(request, "economia/chat.html", {"respuesta": respuesta})


            

import os
import json
import requests
from django.shortcuts import render
from django.conf import settings
from economia.models import Ingreso, Gasto, MetaAhorro

# =======================
# CARGAR JSON UNA VEZ
# =======================
RUTA_JSON = os.path.join(settings.BASE_DIR, "economia", "inflacion.json")

with open(RUTA_JSON, "r", encoding="utf-8") as f:
    DATA_ECONOMICA = json.load(f)


# =======================
# SERIALIZAR DECIMALS → STR
# =======================
def serializar(lista):
    return json.loads(json.dumps(lista, default=str))


# =======================
# OBTENER DATOS DEL USUARIO
# =======================
def obtener_contexto_usuario(usuario):
    ingresos = list(
        Ingreso.objects.filter(usuario=usuario)
        .values("monto", "fuente__nombre", "fecha", "descripcion")
    )

    gastos = list(
        Gasto.objects.filter(usuario=usuario)
        .values("monto", "categoria__nombre", "fecha", "descripcion")
    )

    metas = list(
        MetaAhorro.objects.filter(usuario=usuario)
        .values("nombre_meta", "monto_objetivo", "monto_actual", "estado", "fecha_limite")
    )

    return {
        "ingresos": serializar(ingresos),
        "gastos": serializar(gastos),
        "metas": serializar(metas),
    }


# =======================
#        CHAT LLAMA
# =======================
def chat_llama(request):
    respuesta_texto = None

    if request.method == "POST":
        pregunta = request.POST.get("pregunta", "")

        # Datos JSON generales
        contexto_economico = json.dumps(DATA_ECONOMICA, ensure_ascii=False)

        # Datos del usuario autenticado
        datos_usuario = obtener_contexto_usuario(request.user)
        contexto_usuario = json.dumps(datos_usuario, ensure_ascii=False)

        # === API GROQ ===
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.GROQ_API_KEY}"
        }

        payload = {
            "model": "llama-3.1-8b-instant",
            "max_tokens": 150,      # 150 tokens → respuesta corta
            "temperature": 0.2,     # más directo, menos texto
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Eres un asistente financiero personal. "
                        "Reglas obligatorias:\n"
                        "1) Siempre usa la moneda boliviana 'Bs.' de forma explícita.\n"
                        "2) PROHIBIDO usar símbolos como $, USD, dólares o cualquier otra moneda.\n"
                        "3) Si el usuario no menciona la moneda, asume siempre Bs.\n"
                        "4) Responde siempre en un máximo de 5 líneas.\n"
                        "5) Sé directo, corto y preciso."
                    )
                },
                {
                    "role": "assistant",
                    "content": (
                        "Datos económicos globales:\n" +
                        contexto_economico[:2000] +
                        "\n\nDatos del usuario:\n" +
                        contexto_usuario[:2000]
                    )
                },
                {
                    "role": "user",
                    "content": pregunta
                }
            ]
        }

        try:
            r = requests.post(url, headers=headers, json=payload)
            data = r.json()

            print("DEBUG:", data)

            if "choices" in data:
                respuesta_texto = data["choices"][0]["message"]["content"]
            else:
                respuesta_texto = f"Error en API: {data}"

        except Exception as e:
            respuesta_texto = f"Error inesperado: {e}"

    return render(request, "economia/chat.html", {"respuesta": respuesta_texto})



