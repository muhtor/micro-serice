from .base import *

ALLOWED_HOSTS = ['www.tezbor.uz', 'localhost', 'tezbor.uz', '127.0.0.1', "62.171.185.248", "192.168.0.100",
                 "www.api.tezbor.uz", "api.tezbor.uz", "192.168.0.100", "0171-84-54-84-90.ngrok.io"]

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



