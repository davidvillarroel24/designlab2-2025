from django.urls import path
from .views import IngresoCreateView, IngresoUpdateView,dashboard,registrar_usuario,CategoriaCreateView
from .views import GastoListView, GastoCreateView, GastoUpdateView, GastoDeleteView
from .views import IngresoListView, IngresoDeleteView,CategoriaListView,CategoriaUpdateView,CategoriaDeleteView
from .views import MetaAhorroListView,MetaAhorroCreateView,MetaAhorroUpdateView,MetaAhorroDeleteView
from .views import reporte_generar,reportes_lista,ReporteEliminarView,reporte_pdf
urlpatterns = [     
    
    path('ingresos/nuevo/', IngresoCreateView.as_view(), name='ingreso_nuevo'),
    path('ingresos/<int:pk>/editar/', IngresoUpdateView.as_view(), name='ingreso_editar'),
    path('ingreso/eliminar/<int:pk>/', IngresoDeleteView.as_view(), name='ingreso_eliminar'),
    path('dashboard/', dashboard, name='dashboard'),    
    path('gastos/', GastoListView.as_view(), name='gastos_lista'),
    path('gastos/nuevo/', GastoCreateView.as_view(), name='gasto_nuevo'),
    path('gastos/<int:pk>/editar/', GastoUpdateView.as_view(), name='gasto_editar'),
    path('gastos/<int:pk>/eliminar/', GastoDeleteView.as_view(), name='gasto_eliminar'),
    path('registro/', registrar_usuario, name='registro'),
    path('categorias/nueva/', CategoriaCreateView.as_view(), name='categoria_nueva'),
    path('categoria/<int:pk>/editar/', CategoriaUpdateView.as_view(), name='categoria_editar'),
    path('categoria/<int:pk>/eliminar/', CategoriaDeleteView.as_view(), name='categoria_eliminar'),
    path('categorias/', CategoriaListView.as_view(), name='categorias_lista'),
    path('ingresos/', IngresoListView.as_view(), name='ingresos_lista'),
    path('metas/', MetaAhorroListView.as_view(), name='metas_lista'),
    path('metas/nueva/', MetaAhorroCreateView.as_view(), name='meta_nueva'),
    path('metas/editar/<int:pk>/', MetaAhorroUpdateView.as_view(), name='meta_editar'),
    path('metas/eliminar/<int:pk>/', MetaAhorroDeleteView.as_view(), name='meta_eliminar'),
    path('reportes/generar/', reporte_generar, name='reporte_generar'),
    path('reportes/', reportes_lista, name='reportes_lista'),
    path('reportes/eliminar/<int:pk>/', ReporteEliminarView.as_view(), name='reporte_eliminar'),
    path('reportes/pdf/<int:reporte_id>/', reporte_pdf, name='reporte_pdf'),


]