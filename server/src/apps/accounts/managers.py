from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from apps.core.services.model_status import UserStatus, UserType
from django.contrib.auth.models import BaseUserManager
from apps.core.services.geo_api import GeoLocationApi


class UserManager(BaseUserManager, GeoLocationApi):
    def create_user(self, phone_number, password=None, _type=UserType.CUSTOMER, is_superuser=False):
        if is_superuser:
            country = self.get_prefix_country(prefix=None)
            user = self.model(phone_number=phone_number, country=country, type=_type)
        else:
            user = self.model(phone_number=phone_number, type=_type)
        if not phone_number:
            raise ValueError('Users must have a phone number')
        if password is not None:
            user.set_password(password)
        user.status = UserStatus.NOTACTIVATED
        user.is_superuser = is_superuser
        user.save()
        return user

    def create_staffuser(self, phone_number, password):
        if not password:
            raise ValueError('staff/admins must have a password.')
        user = self.create_user(phone_number=phone_number, password=password)
        user.is_staff = True
        user.save()
        return user

    def create_superuser(self, phone_number, password):
        if not password:
            raise ValueError('superusers must have a password.')
        user = self.create_user(phone_number=phone_number, password=password, _type=UserType.ADMIN, is_superuser=True)
        user.is_active = True
        user.status = UserStatus.ACTIVATED
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user

    def get_prefix_country(self, prefix):
        return self.get_country(prefix=prefix)


class PhoneActivationQuerySet(models.query.QuerySet):
    def confirmable(self):
        now = timezone.now()
        start_range = now - timedelta(minutes=3)
        end_range = now
        return self.filter(timestamp__gt=start_range, timestamp__lte=end_range)

    def is_confirmable(self, phone):
        now = timezone.now()
        start_range = now - timedelta(days=7)
        return self.filter(phone=phone).filter(timestamp__gt=start_range, timestamp__lte=now)


class PhoneActivationManager(models.Manager):
    def get_queryset(self):
        return PhoneActivationQuerySet(self.model, using=self._db)

    def confirmable(self):
        return self.get_queryset().confirmable()

    def phone_exists(self, phone):
        return self.get_queryset().filter(Q(user__phone_number=phone) | Q(user__phone_number=phone))