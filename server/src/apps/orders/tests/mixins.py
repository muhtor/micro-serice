from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse
from apps.core.services.model_status import *
from apps.core.services.generics import TBResponse
from apps.core.authentication.tb_auth import TBUserToken
from apps.addresses.services import generator_random_phone_number

ORDER_CREATE_URL = reverse("orders:parcel_create")
ORDER_UPDATE_STS_URL = reverse("orders:order_status_update")

ORDER_CREATE_PAYLOAD = {
    "sender_name": "Eshmat",
    "sender_phone": "+998901110000",
    "receiver_name": "Toshmat",
    "receiver_phone": "+998990000000",
    "description": "Test Order",
    "from": {
        "name": "Tashkent bodomzor",
        "address1": "bodomzor ko'chasi",
        "latitude": 41.333326,
        "longitude": 69.284367,
        "city": "Tashkent",
        "full_name": "Tashkent Uzbekistan",
        "phone_number": "+998901234567",
        "type": AddressType.DOOR
    },
    "to": {
        "name": "Shodlik",
        "address1": "Alisher ko'chasi",
        "latitude": 40.992122,
        "longitude": 71.650697,
        "city": "Namangan",
        "full_name": "Namangan, Uzbekistan",
        "phone_number": "+998901234567",
        "type": AddressType.DOOR
    },
    "parcel_size": {
        "weight": 1.7,
        "width": 30.0,
        "height": 50.0,
        "length": 60.0
    },
    "delivery_option": DeliveryType.EXPRESS,
    "images": [1]
}


def create_user(**params):
    return get_user_model().objects.create(**params)


class TestCaseMixin(TestCase):

    def setUp(self):
        self.user = create_user(phone_number=f"+998{generator_random_phone_number()}", username="faster")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        token = TBUserToken.objects.create(user=self.user).key
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
