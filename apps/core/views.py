from django.shortcuts import render

from .models import ConfiguracionGimnasio
from apps.actividades.models import Actividad
# El contenido de "ventajas", "clases" y "planes" es copy de marketing para
# la landing y no tiene todavía un modelo propio (no hay campos como
# "beneficios" o "destacado" en apps.membresias.Plan), así que se mantiene
# acá. Si en el futuro se necesita editar precios/beneficios sin tocar
# código, esos campos deberían agregarse a Plan y esta vista debería leer
# de ahí en lugar de esta lista fija.
VENTAJAS = [
    {
        "icono": "fa-solid fa-dumbbell",
        "titulo": "Equipamiento moderno",
        "texto": "Máquinas y equipos de última generación, mantenidos y renovados constantemente para tu seguridad y rendimiento.",
    },
    {
        "icono": "fa-solid fa-heart-pulse",
        "titulo": "Plan nutricional saludable",
        "texto": "Acompañamos tu entrenamiento con pautas de alimentación pensadas junto a profesionales del área.",
    },
    {
        "icono": "fa-solid fa-user-graduate",
        "titulo": "Entrenamiento profesional",
        "texto": "Profesores capacitados que diseñan rutinas adaptadas a cada objetivo, desde principiantes hasta avanzados.",
    },
    {
        "icono": "fa-solid fa-bullseye",
        "titulo": "A tu medida",
        "texto": "Cada cuerpo es distinto: adaptamos intensidad, cargas y progresión a tus necesidades particulares.",
    },
]

CLASES = [
    {"categoria": "Fuerza", "nombre": "Musculación", "img": "class-1"},
    {"categoria": "Cardio", "nombre": "Ciclismo indoor", "img": "class-2"},
    {"categoria": "Fuerza", "nombre": "Kettlebells", "img": "class-3"},
    {"categoria": "Cardio", "nombre": "Funcional", "img": "class-4"},
    {"categoria": "Entrenamiento", "nombre": "Boxeo", "img": "class-5"},
]

PLANES = [
    {
        "nombre": "Clase suelta",
        "precio": "3.500",
        "detalle": "POR CLASE",
        "beneficios": [
            "Acceso a sala de musculación",
            "Equipamiento sin límite",
            "Sin permanencia mínima",
        ],
        "destacado": False,
    },
    {
        "nombre": "Mensual full",
        "precio": "18.000",
        "detalle": "POR MES",
        "beneficios": [
            "Acceso ilimitado todo el mes",
            "Todas las clases grupales",
            "Seguimiento de un profesor",
            "Sin horarios restringidos",
        ],
        "destacado": True,
    },
    {
        "nombre": "Trimestral",
        "precio": "48.000",
        "detalle": "CADA 3 MESES",
        "beneficios": [
            "Acceso ilimitado",
            "Plan de entrenamiento personalizado",
            "Evaluación física mensual",
        ],
        "destacado": False,
    },
]

# Valores de respaldo por si la tabla ConfiguracionGimnasio está vacía
# (por ejemplo, en un entorno nuevo donde todavía no corrió la migración
# de datos apps.core.0002).
_CONFIG_POR_DEFECTO = {
    "nombre": "Malvinas Gym",
    "barrio": "Barrio Piedrabuena",
    "direccion": "Barrio Piedrabuena, Ciudad Autónoma de Buenos Aires",
    "telefono": "11 2560-8817",
    "email": "contacto@malvinasgym.com.ar",
    "instagram": "@malvinasgym",
}


def index(request):
    """Home pública del gimnasio.

    Antes los datos de contacto estaban hardcodeados acá mismo, duplicando
    el modelo ConfiguracionGimnasio (que existe pero nunca se leía). Ahora
    se consulta la fila real, y solo se cae al valor por defecto si la
    tabla está vacía.
    """
    configuracion = ConfiguracionGimnasio.objects.first()

    if configuracion is not None:
        gimnasio = {
            "nombre": configuracion.nombre,
            "barrio": configuracion.barrio,
            "direccion": configuracion.direccion,
            "telefono": configuracion.telefono,
            "email": configuracion.email,
            "instagram": configuracion.instagram,
        }
    else:
        gimnasio = _CONFIG_POR_DEFECTO

    clases = (
    Actividad.objects
    .filter(estado_actividad__nombre__iexact="Activo")
    .order_by("nombre")[:6]
)

    context = {
        "gimnasio": gimnasio,
        "ventajas": VENTAJAS,
        "clases": clases,
        "planes": PLANES,
    }

    return render(request, "core/index.html", context)
