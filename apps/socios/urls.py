from django.urls import path
from . import views

app_name = "socios"

urlpatterns = [
    path("", views.lista_socios, name="lista"),
    path("nuevo/", views.crear_socio, name="crear"),

    path("<int:pk>/", views.detalle_socio, name="detalle"),
    path("<int:pk>/editar/", views.editar_socio, name="editar"),

    # Cambios de estado
    path("<int:pk>/activar/", views.activar_socio, name="activar"),
    path("<int:pk>/suspender/", views.suspender_socio, name="suspender"),
    path("<int:pk>/reanudar/", views.reanudar_socio, name="reanudar"),
    path("<int:pk>/dar-baja/", views.dar_baja_socio, name="dar_baja"),
    path("<int:pk>/reactivar/", views.reactivar_socio, name="reactivar"),

    # Eliminación definitiva
    path("<int:pk>/eliminar/", views.eliminar_socio, name="eliminar"),
]