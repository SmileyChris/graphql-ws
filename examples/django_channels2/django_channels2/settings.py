"""
Django settings for django_channels2 project.
"""
SECRET_KEY = "0%1c709jhmggqhk&=tci06iy+%jedfxpcoai69jd8wjzm+k2f0"
DEBUG = True


INSTALLED_APPS = [
    "channels",
    "graphql_ws.django",
    "graphene_django",
    "django_channels2",
    "django.contrib.staticfiles",
    # "django.contrib.sessions",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
    }
]

MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
]

STATIC_URL = "/static/"
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
ROOT_URLCONF = "django_channels2.urls"
ASGI_APPLICATION = "graphql_ws.django.routing.session_application"

CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}
GRAPHENE = {"MIDDLEWARE": [], "SCHEMA": "django_channels2.schema.schema"}
