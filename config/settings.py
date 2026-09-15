"""
Django settings for the Malvinas GYM project.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/topics/settings/
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Carga las variables de entorno desde el archivo .env (una sola vez).
# Ver .env.example para la lista completa de variables soportadas.
load_dotenv(BASE_DIR / ".env")

# SECURITY WARNING: keep the secret key used in production secret!
# En desarrollo, si no existe DJANGO_SECRET_KEY en el entorno, se usa un
# valor de relleno claramente marcado como inseguro para que nadie lo use
# por error en un despliegue real.
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-solo-para-desarrollo-local-no-usar-en-produccion",
)

# SECURITY WARNING: don't run with debug turned on in production!
# Por defecto False: hay que activarlo explícitamente en desarrollo (.env)
# para evitar que un despliegue real quede con DEBUG=True por descuido.
DEBUG = os.getenv("DJANGO_DEBUG", "False") == "True"

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")
    if host.strip()
]

# SECURITY WARNING: si DEBUG está en False (producción) y todavía se está
# usando la SECRET_KEY de relleno de arriba, es un despliegue mal
# configurado: frenamos el arranque en vez de dejarlo pasar en silencio.
if not DEBUG and SECRET_KEY == "django-insecure-solo-para-desarrollo-local-no-usar-en-produccion":
    raise RuntimeError(
        "DJANGO_SECRET_KEY no está definida en el entorno y DEBUG=False. "
        "Configurá una SECRET_KEY real antes de desplegar a producción."
    )

# Orígenes autorizados a enviar POST con CSRF (dominio real del panel en
# producción, detrás de HTTPS). Se define por variable de entorno para no
# hardcodear el dominio del gimnasio en el repo.
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]

# ---------------------------------------------------------------------
# Endurecimiento HTTP en producción (DEBUG=False). En desarrollo local se
# deja todo apagado para no romper el flujo por HTTP sin certificado.
# ---------------------------------------------------------------------
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True
    SECURE_SSL_REDIRECT = os.getenv("DJANGO_SECURE_SSL_REDIRECT", "True") == "True"
    SECURE_HSTS_SECONDS = int(os.getenv("DJANGO_SECURE_HSTS_SECONDS", "31536000"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = "same-origin"
    X_FRAME_OPTIONS = "DENY"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    CSRF_COOKIE_SAMESITE = "Lax"

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Apps de Malvinas GYM
    "apps.core.apps.CoreConfig",
    "apps.usuarios.apps.UsuariosConfig",
    "apps.socios.apps.SociosConfig",
    "apps.actividades.apps.ActividadesConfig",
    "apps.membresias.apps.MembresiasConfig",
    "apps.cuotas.apps.CuotasConfig",
    "apps.caja.apps.CajaConfig",
    "apps.notificaciones.apps.NotificacionesConfig",
    "apps.dashboard.apps.DashboardConfig",
]

AUTH_USER_MODEL = "usuarios.Usuario"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Única fuente de plantillas del proyecto: MalvinasGym-main/templates/.
        # Ninguna app dentro de apps/ debe tener su propia carpeta
        # templates/ (eso generaba duplicados y referencias cruzadas
        # inconsistentes entre apps/core/templates y esta carpeta global).
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/6.1/ref/settings/#databases
#
# Postgres en todos los entornos, con credenciales desde el .env (nunca
# hardcodeadas). En desarrollo local, si no se define DB_NAME, se cae a
# un sqlite de archivo para poder levantar el proyecto sin instalar
# Postgres — pensado solo para probar rápido, no reemplaza probar contra
# Postgres real antes de un despliegue.
if os.getenv("DB_NAME"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME"),
            "USER": os.getenv("DB_USER"),
            "PASSWORD": os.getenv("DB_PASSWORD"),
            "HOST": os.getenv("DB_HOST", "localhost"),
            "PORT": os.getenv("DB_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Password validation
# https://docs.djangoproject.com/en/6.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.1/topics/i18n/
# El gimnasio opera en CABA, Argentina: localizar idioma y huso horario.

LANGUAGE_CODE = "es-ar"

TIME_ZONE = "America/Argentina/Buenos_Aires"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.1/howto/static-files/

STATIC_URL = "static/"

# Única fuente de estáticos del proyecto: MalvinasGym-main/static/.
# Antes existía además apps/core/static/, y como STATICFILES_DIRS no
# estaba definido acá, Django solo veía la copia de apps/core (vía
# AppDirectoriesFinder) e ignoraba por completo esta carpeta global, así
# que dos versiones de los mismos archivos convivían y se desincronizaban
# sin que nadie lo notara. Ahora hay una sola carpeta real y Django la
# encuentra explícitamente con FileSystemFinder.
STATICFILES_DIRS = [BASE_DIR / "static"]

# Carpeta donde `collectstatic` reúne todos los archivos para producción.
# No debe versionarse en git (ver .gitignore) ni confundirse con
# STATICFILES_DIRS, que es la fuente real de los archivos en desarrollo.
STATIC_ROOT = BASE_DIR / "staticfiles"

# Archivos subidos por usuarios (ej. apto físico de los socios).
# Antes no existía esta configuración: los FileField no tenían dónde
# guardar los archivos de forma confiable.
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Autenticación
# El panel de gestión (apps/socios y las que se sumen después) requiere
# login. Se usan las vistas de auth que trae Django
# (django.contrib.auth.urls) en vez de reinventarlas.
LOGIN_URL = "login"
# Tras iniciar sesión, el destino por defecto es el Dashboard (no un
# módulo de gestión puntual como socios). Al cerrar sesión, se vuelve a
# la home pública del sitio.
LOGIN_REDIRECT_URL = "dashboard:index"
LOGOUT_REDIRECT_URL = "core:index"


# Email
# https://docs.djangoproject.com/en/6.1/topics/email/#topic-email-configuration
#
# En desarrollo los mails se imprimen por consola. En producción, definir
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend y las
# variables EMAIL_HOST/EMAIL_HOST_USER/EMAIL_HOST_PASSWORD en el .env.
EMAIL_BACKEND = os.getenv(
    "DJANGO_EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",
)
