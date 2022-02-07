from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.core.authentication.tb_auth import TBUserToken
from rest_framework.test import APIClient
from apps.core.services.model_status import *
from apps.core.services.generics import TBResponse
from apps.addresses.services import generator_random_phone_number


def create_user(**params):
    return get_user_model().objects.create(**params)


class TestCaseMixin(TestCase):

    def setUp(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs['user']
        else:
            self.user = create_user(phone_number=f"+998{generator_random_phone_number()}", username="faster")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        token = TBUserToken.objects.create(user=self.user).key
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        return self.user

