from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.actividades.models import Actividad
from apps.socios.models import Socio


@login_required
def index(request):
    """Pantalla de aterrizaje tras iniciar sesión.

    Antes LOGIN_REDIRECT_URL apuntaba directo a socios:lista, lo que
    mezclaba "iniciar sesión" con "gestionar socios". Esta vista da un
    punto de entrada neutral al panel de gestión, con un resumen rápido
    del estado del gimnasio y accesos directos a los módulos más usados.
    """
    total_socios = Socio.objects.count()
    socios_activos = Socio.objects.filter(estado_socio__nombre__iexact="Activo").count()
    total_actividades = Actividad.objects.count()
    actividades_activas = Actividad.objects.filter(
        estado_actividad__nombre__iexact="Activo"
    ).count()

    contexto = {
        "total_socios": total_socios,
        "socios_activos": socios_activos,
        "total_actividades": total_actividades,
        "actividades_activas": actividades_activas,
    }

    return render(request, "dashboard/index.html", contexto)
