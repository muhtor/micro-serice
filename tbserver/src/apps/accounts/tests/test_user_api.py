from django.urls import reverse
from apps.addresses.services import DataPreparer, generator_random_phone_number
from apps.accounts.models import UserCar
from apps.core.services.model_status import UserCarType, UserCarColor, UserCarStatus
from .mixins import *

CREATE_USER_URL = reverse("accounts:create")
CREATE_DRIVER_URL = reverse("accounts:driver_create")
CREATE_USER_CAR_URL = reverse("accounts:car_create")

CREATE_CAR_PAYLOAD = {
    "name": "cobalt",
    "model": "car model",
    "type": UserCarType.SEDAN,
    "passenger_count": 4,
    "number": "506",
    "color": UserCarColor.WHITE,
    "tech_pass_id": "123456"
}


class PublicUserApiTests(TestCaseMixin):
    """Test the users API (public)"""

    PAYLOAD = {"phone_number": f"+998{generator_random_phone_number()}", "username": "tezbor"}

    def test_create_valid_data(self):
        res = self.client.post(CREATE_USER_URL, self.PAYLOAD, format="json")

        self.assertTrue(res.data['success'])
        self.assertEqual(res.data['code'], TBResponse.CODE_0)

    def test_create_invalid_data(self):
        """ invalid prefix or not + in phone number ... code 13"""
        invalid_data = {"phone_number": "998901234561", "username": "tezbor"}
        res = self.client.post(CREATE_USER_URL, invalid_data, format="json")
        self.assertFalse(res.data['success'])
        self.assertEqual(res.data['code'], TBResponse.CODE_6)

    def test_user_exists(self):
        """ this phone number awaiting activation ... code 7"""
        create_user(**self.PAYLOAD)
        res = self.client.post(CREATE_USER_URL, self.PAYLOAD, format="json")
        self.assertFalse(res.data['success'])
        self.assertEqual(res.data['code'], TBResponse.CODE_7)


class UserCarCreateTests(TestCaseMixin):

    def test_create_car(self):
        res = self.client.post(CREATE_USER_CAR_URL, CREATE_CAR_PAYLOAD, format="json")
        self.assertTrue(res.data["success"])
        self.assertEqual(res.data["results"]["driver"], self.user.id)


class UserCarRetrieveUpdateDestroyTests(TestCaseMixin):
    data_preparer = DataPreparer()

    def test_update_car(self):
        self.client.post(CREATE_USER_CAR_URL, CREATE_CAR_PAYLOAD, format="json")
        self.data_preparer.create_driver()
        update_car_url = reverse("accounts:car_retrieve", args=[UserCar.objects.first().id])

        payload = CREATE_CAR_PAYLOAD.copy()
        payload["name"] = "nexia"
        res = self.client.put(update_car_url, payload, format="json")
        car_from_db = UserCar.objects.get(pk=res.data["data"]["id"])
        self.assertTrue(res.data["success"])
        self.assertEqual(payload["name"], car_from_db.name)

    def test_retrieve_car(self):
        self.data_preparer.create_driver()
        self.client.post(CREATE_USER_CAR_URL, CREATE_CAR_PAYLOAD, format="json")
        res = self.client.get(reverse("accounts:car_retrieve", args=[UserCar.objects.first().id]))
        self.assertTrue(res.data["success"])

    def test_destroy_car(self):
        self.data_preparer.create_driver()
        self.client.post(CREATE_USER_CAR_URL, CREATE_CAR_PAYLOAD, format="json")
        car_id = UserCar.objects.first().id
        res = self.client.delete(reverse("accounts:car_retrieve", args=[car_id]))
        car_from_db = UserCar.objects.get(pk=car_id)
        self.assertTrue(res.data["success"])
        self.assertEqual(UserCarStatus.DELETED, car_from_db.status)
