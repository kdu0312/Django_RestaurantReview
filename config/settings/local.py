from .base import *  # noqa: F403
from .base import SECRET
import os


def _bool(v: str, default=False):
    if v is None:
        return default
    return v.strip().lower() in {"1", "true", "yes", "y", "on"}


DEBUG = _bool(os.getenv("DEBUG"), True)
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")
ALLOWED_HOSTS = [h.strip() for h in ALLOWED_HOSTS if h.strip()]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", SECRET["DB"]["NAME"]),
        "USER": os.getenv("POSTGRES_USER", SECRET["DB"]["USER"]),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", SECRET["DB"]["PASSWORD"]),
        "HOST": os.getenv("POSTGRES_HOST", SECRET["DB"]["HOST"]),
        "PORT": os.getenv("POSTGRES_PORT", str(SECRET["DB"]["PORT"])),
    }
}
