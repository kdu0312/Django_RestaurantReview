# config/settings/prod.py
# ruff: noqa: F401, F403
from .base import *
import os

DEBUG = False

# 스킴/포트 없이 "도메인 또는 IP"만 넣어야 함
ALLOWED_HOSTS = [
    "YOUR_USERNAME.pythonanywhere.com",
    "yourdomain.com",
    "www.yourdomain.com",
]

# DB: 배포 시작은 SQLite로 OK, 이후 MySQL/Postgres로 전환 권장
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
# (나중에 전환 시)
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.mysql",
#         "NAME": SECRET["DB"]["NAME"],
#         "USER": SECRET["DB"]["USER"],
#         "PASSWORD": SECRET["DB"]["PASSWORD"],
#         "HOST": SECRET["DB"]["HOST"],
#         "PORT": SECRET["DB"]["PORT"],
#     }
# }

# 정적/미디어
# URL은 앞에 슬래시 `/`를 붙이는 게 정석
STATIC_URL = "/static/"
MEDIA_URL = "/media/"

# 배포에서는 collectstatic 결과만 서빙 → STATICFILES_DIRS는 보통 생략
# (개발용 정적 경로 모을 필요 X)
STATIC_ROOT = BASE_DIR / "staticfiles"  # python manage.py collectstatic 타겟
MEDIA_ROOT = BASE_DIR / "mediafiles"  # PythonAnywhere에서 media 매핑

# (HTTPS 쓸 때 권장)
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# CSRF_TRUSTED_ORIGINS = ["https://YOUR_USERNAME.pythonanywhere.com", "https://yourdomain.com", "https://www.yourdomain.com"]
