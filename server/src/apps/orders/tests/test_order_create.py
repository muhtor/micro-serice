from django.core.management import call_command
from apps.addresses.services import DataPreparer
from .mixins import *


class CreateOrderWithAnonymousUser(TestCase, DataPreparer):

    def test_public_create_order_without_key_from(self):
        del ORDER_CREATE_PAYLOAD["from"]
        res = self.client.post(
            path=ORDER_CREATE_URL,
            data=ORDER_CREATE_PAYLOAD,
            content_type="application/json")
        self.assertFalse(res.data["success"])
        self.assertEqual(res.data["code"], TBResponse.CODE_3)

    def test_public_create_order_without_key_to(self):
        del ORDER_CREATE_PAYLOAD["to"]
        self.upload_file()
        res = self.client.post(
            path=ORDER_CREATE_URL,
            data=ORDER_CREATE_PAYLOAD,
            content_type="application/json")
        self.assertFalse(res.data["success"])
        self.assertEqual(res.data["code"], TBResponse.CODE_3)

    def test_public_create_order_with_invalid_delivery_type(self):
        ORDER_CREATE_PAYLOAD["delivery_option"] = 10
        res = self.client.post(
            path=ORDER_CREATE_URL,
            data=ORDER_CREATE_PAYLOAD,
            content_type="application/json")
        # print("Res...", res.data)
        self.assertFalse(res.data["success"])
        self.assertEqual(res.data["code"], TBResponse.CODE_3)

    def test_public_create_order_success(self):
        data = ORDER_CREATE_PAYLOAD
        self.upload_file()
        res = self.client.post(
            path=ORDER_CREATE_URL,
            data=data,
            content_type="application/json")
        # print("test_public_create_order_success...", res.data)
        self.assertTrue(res.data["success"])


class CreateOrderWithAuthenticatedUser(TestCaseMixin, DataPreparer):

    def test_private_create_order_with_invalid_region(self):
        data = {
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
                "city": "TTT",  # invalid region name
                "full_name": "Tashkent Uzbekistan",
                "phone_number": "+998901234567",
                "type": 1
            },
            "to": {
                "name": "Shodlik",
                "address1": "Alisher ko'chasi",
                "latitude": 40.992122,
                "longitude": 71.650697,
                "city": "Namangan",
                "full_name": "Namangan, Uzbekistan",
                "phone_number": "+998901234567",
                "type": 1
            },
            "parcel_size": {
                "weight": 2.7,
                "width": 30.0,
                "height": 50.0,
                "length": 60.0
            },
            "delivery_option": DeliveryType.EXPRESS,
            "images": None
        }
        res = self.client.post(path=ORDER_CREATE_URL, data=data, format='json')
        print("RES...", res.data)
        self.assertFalse(res.data["success"])
        self.assertEqual(res.data["code"], TBResponse.CODE_6)

    def test_private_create_order_success(self):
        image = self.upload_file()
        data = {
            "sender_name": "Eshmat",
            "sender_phone": "+998901111111",
            "receiver_name": "Toshmat",
            "receiver_phone": "+998902222222",
            "description": "Bu test uchun yaratilgan Order",
            "from": {
                "name": "Boboraxim Mashrab ko'chasi",
                "address1": "Street Alisher navoiy 34a",
                "latitude": 41.000085,
                "longitude": 71.672579,
                "city": "Namangan",
                "full_name": "Eshamtoff",
                "phone_number": "+998901234567",
                "type": AddressType.DOOR
            },
            "to": {
                "name": "Boboraxim Mashrab ko'chasi",
                "address1": "Street Alisher navoiy 34a",
                "latitude": 41.002611,
                "longitude": 71.677306,
                "city": "Tashkent",
                "full_name": "Toshmatoff",
                "phone_number": "+998901234567",
                "type": AddressType.DOOR
            },
            "parcel_size": {
                "weight": 10,
                "width": 10,
                "height": 10,
                "length": 10
            },
            "delivery_option": DeliveryType.EXPRESS,
            "images": [image.pk]
        }
        res = self.client.post(path=ORDER_CREATE_URL, data=data, format='json')
        self.assertTrue(res.data["success"])
        self.assertEqual(res.data["code"], TBResponse.CODE_0)

    def test_private_create_order_with_identical_address(self):
        image = self.upload_file()
        data = {
            "sender_name": "Eshmat",
            "sender_phone": "+998901111111",
            "receiver_name": "Toshmat",
            "receiver_phone": "+998902222222",
            "description": "Bu test uchun yaratilgan Order",
            "from": {
                "name": "Boboraxim Mashrab ko'chasi",
                "address1": "Street Alisher navoiy 34a",
                "latitude": 41.000569,
                "longitude": 71.664307,
                "city": "Namangan",
                "full_name": "Eshamtoff",
                "phone_number": "+998901234567",
                "type": AddressType.DOOR
            },
            "to": {
                "name": "Boboraxim Mashrab ko'chasi",
                "address1": "Street Alisher navoiy 34a",
                "latitude": 41.000569,
                "longitude": 71.664307,
                "city": "Tashkent",
                "full_name": "Toshmatoff",
                "phone_number": "+998901234567",
                "type": AddressType.DOOR
            },
            "parcel_size": {
                "weight": 10,
                "width": 10,
                "height": 10,
                "length": 10
            },
            "delivery_option": DeliveryType.EXPRESS,
            "images": [image.pk]
        }
        res = self.client.post(path=ORDER_CREATE_URL, data=data, format='json')
        self.assertFalse(res.data["success"])
        self.assertEqual(res.data["code"], TBResponse.CODE_55)
