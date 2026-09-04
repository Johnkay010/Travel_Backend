"""
Django settings for hebron_backend project.

Security-sensitive values (SECRET_KEY, DEBUG, ALLOWED_HOSTS,
CORS_ALLOWED_ORIGINS) read from environment variables
first and fall back to the values below, which match this project's
existing Render deployment + local dev setup — so nothing breaks if you
don't set anything. See README's "Deploying live" section for what to set
on Render and Netlify.
"""

import os

import dj_database_url
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _env_list(name, default):
    """Read a comma-separated env var into a list, e.g.
    ALLOWED_HOSTS=example.com,www.example.com
    Falls back to `default` (a list) if the env var isn't set.
    """
    raw = os.environ.get(name)
    if not raw:
        return default
    return [item.strip() for item in raw.split(",") if item.strip()]


# --- Security -----------------------------------------------------------
# Set a real SECRET_KEY as an env var in production — never reuse this
# fallback outside local dev. Generate one with:
#   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-prototype-key-change-me")

# IMPORTANT: this is currently True by default, which is fine locally but
# NOT safe on a public Render URL — it leaks stack traces and settings to
# any visitor who triggers an error. Set DEBUG=False in Render's
# Environment tab now if you haven't already.
DEBUG = os.environ.get("DEBUG", "True") == "True"

ALLOWED_HOSTS = _env_list(
    "ALLOWED_HOSTS",
    ["localhost", "127.0.0.1", "travel-backend-bcty.onrender.com"],
)

# --- Applications ---------------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "leads",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Whitenoise serves collected static files (admin CSS, etc.) directly
    # from Django on Render — must sit right after SecurityMiddleware and
    # before everything else per whitenoise's own docs.
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "hebron_backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "hebron_backend.wsgi.application"

# --- Database ---------------------------------------------------------
# Defaults to local SQLite. If a DATABASE_URL env var is set (e.g. Render's
# managed Postgres connection string), that takes over instead — you
# already have psycopg2-binary + dj-database-url installed, so this is
# ready to go the moment you attach a Postgres instance on Render.
#
# Worth doing soon if you're on Render: their free web services have an
# EPHEMERAL disk, meaning a plain SQLite file gets wiped on every deploy
# and periodic restart — any leads/payments collected would vanish. Until
# a real Postgres is attached, treat SQLite-on-Render as demo-only, not a
# reliable store.
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- CORS ---------------------------------------------------------
# Add your deployed FRONTEND's origin here (or via env var) once you have
# one — e.g. CORS_ALLOWED_ORIGINS=https://your-site.netlify.app. The
# travel-backend-bcty.onrender.com entry below is the backend's own
# domain; keep it only if something (e.g. Django admin) calls the API
# from that same origin.
CORS_ALLOWED_ORIGINS = _env_list(
    "CORS_ALLOWED_ORIGINS",
    [
        "http://localhost:5173",
        "http://127.0.0.1:5173",

        "https://hebronalliance.netlify.app",
    ],
)
CSRF_TRUSTED_ORIGINS = _env_list(
    "CSRF_TRUSTED_ORIGINS",
    [
        "http://localhost:5173",
        "http://127.0.0.1:5173",

        "https://hebronalliance.netlify.app",
    ],
)

# --- DRF ---------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}
