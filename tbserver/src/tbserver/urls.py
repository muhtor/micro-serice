"""src URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import datetime

from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
# Swagger documentation setup
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from apps.billing.models import create_invoice_for_merchants
from apps.dashboard.views import LoginView
from apps.dashboard.views import LogoutView
from apps.dashboard.views import HomePageUZView
from apps.dashboard.views import HomePageOZView
from apps.dashboard.views import HomePageRUView
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required

from apps.queues.jobs.scheduler import scheduler

schema_view = get_schema_view(
    openapi.Info(
        title="TEZBOR API",
        default_version='v1',
        description="TEZBOR Documentations",
        terms_of_service="https://tezbor.uz/",
        contact=openapi.Contact(email="admin@gmail.com", phone="+998901234567"),
        license=openapi.License(name="MIT License"),
    ),
    public=False,
)

urlpatterns = [
    path('secretaccessadmin/', admin.site.urls),
    # Home page
    path('login/', LoginView.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('', HomePageRUView.as_view(), name="home_ru"),
    path("uz", HomePageUZView.as_view(), name="home_uz"),
    path("oz", HomePageOZView.as_view(), name="home_oz"),
    path("ru", HomePageRUView.as_view(), name="home_ru"),
    path('dashboard/', include('apps.dashboard.urls')),

    # path('api/djoser/v1/', include('djoser.urls')),
    # path('api/djoser/v1/', include('djoser.urls.authtoken')),
    # for browsable API - login and logout
    # path('api-auth', include('rest_framework.urls')),

    path('api/accounts/', include('apps.accounts.api.urls')),
    path('api/addresses/', include('apps.addresses.api.urls')),
    path('api/billing/', include('apps.billing.api.urls')),
    path('api/orders/', include('apps.orders.api.urls')),
    path('api/uploads/', include('apps.uploads.api.urls')),
    path('api/dashboard/', include('apps.dashboard.api.urls')),
    # DOCS
    # path('docs/', include_docs_urls(title='TEZBOR Api')),
    url(r'^api/docs(?P<format>\.json|\.yaml)$', login_required(schema_view.without_ui(cache_timeout=0)), name='schema-json'),
    url(r'^api/docs/$', login_required(schema_view.with_ui('swagger', cache_timeout=0)), name='schema-swagger-ui'),
    url(r'^redoc/$', login_required(schema_view.with_ui('redoc', cache_timeout=0)), name='schema-redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


scheduler.add_job(create_invoice_for_merchants, trigger='cron', month="*", day="1", hour="04", minute="00")
# scheduler.add_job(remove_inv_id, trigger='date',
#                   run_date=datetime.datetime.now() + datetime.timedelta(minutes=1))