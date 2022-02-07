import os

from tbserver.settings.base import *
from tbserver.aws.conf import *

DEBUG = True


ALLOWED_HOSTS = [
    "www.tezbor.uz", "localhost", "tezbor.uz", "127.0.0.1", "api.tezbor.uz", "62.171.185.248",
    "test.tezbor.uz", "api.staging.tezbor.uz", "prod.tezbor.uz", "gobazar.uz", "192.168.0.100",
    "opencart.kelajakimorat.uz", "kitoblardunyosi.uz"
]

DATABASES = {
    'default': {
        "ENGINE": os.environ.get("SQL_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("SQL_DATABASE", os.path.join(BASE_DIR, "db.sqlite3")),
        "USER": os.environ.get("SQL_USER", "tb_user"),
        "PASSWORD": os.environ.get("SQL_PASSWORD", "tb_pass"),
        "HOST": os.environ.get("SQL_HOST", "tezdb"),
        "PORT": os.environ.get("SQL_PORT", "5432"),
    }
}