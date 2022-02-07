from apps.accounts.tests.mixins import *
from apps.addresses.models import Address
from django.urls import reverse

ADDRESS_LIST_URL = reverse("addresses:address_list")
ADDRESS_CREATE_URL = reverse("addresses:address_create")
ADDRESS_CREATE_PAYLOAD = {
    "name": "Chinor",
    "address1": "Sardoba district",
    "address2": "Наманган, Узбекистан",
    "latitude": 41.004391,
    "longitude": 71.681497,
    "city": "Namangan",
    "email": "test@gmail.com",
    "full_name": "toshmat-off",
    "phone_number": "+998000000001",
    "type": 2
}


class AddressCreateTests(TestCaseMixin):

    def test_create(self):
        res = self.client.post(ADDRESS_CREATE_URL, ADDRESS_CREATE_PAYLOAD, format="json")
        self.assertTrue(res.data["success"])

        address_from_db = Address.objects.get(pk=res.data["result"]["id"])
        self.assertIsNotNone(address_from_db)
        self.assertEqual(address_from_db.name, res.data["result"]["name"])


class AddressRetrieveUpdateDestroyTests(TestCaseMixin):
    def test_retrieve(self):
        self.client.post(ADDRESS_CREATE_URL, ADDRESS_CREATE_PAYLOAD, format="json")
        reverse_url = reverse("addresses:address_rud", args=[Address.objects.first().id])
        res = self.client.get(reverse_url)
        self.assertTrue(res.data["success"])

    def test_destroy(self):
        self.client.post(ADDRESS_CREATE_URL, ADDRESS_CREATE_PAYLOAD, format="json")
        address_id = Address.objects.first().id
        reverse_url = reverse("addresses:address_rud", args=[address_id])
        res = self.client.delete(reverse_url)
        self.assertTrue(res.data["success"])
        address_from_db = Address.objects.get(pk=address_id)
        self.assertEqual(AddressStatus.DELETED, address_from_db.status)

    def test_update_fail(self):
        self.client.post(ADDRESS_CREATE_URL, ADDRESS_CREATE_PAYLOAD, format="json")
        reverse_url = reverse("addresses:address_rud", args=[Address.objects.first().id])
        payload = {
            "name": "Another Address",
            "address1": "Street Alisher navoiy",
            "email": "test@gmail.com",
            "full_name": "some name",
            "phone_number": "+998000000001",
            "status": AddressStatus.ACTIVE}
        res = self.client.put(reverse_url, payload, format="json")
        self.assertEqual(400, res.status_code)

    def test_get_delete_fail(self):
        reverse_url = reverse("addresses:address_rud", args=[1])
        res = self.client.get(reverse_url)
        self.assertFalse(res.data["success"])
        res = self.client.delete(reverse_url)
        self.assertFalse(res.data["success"])


class AddressListTests(TestCaseMixin):

    def test_list_success(self):
        self.client.post(ADDRESS_CREATE_URL, ADDRESS_CREATE_PAYLOAD, format="json")
        self.client.post(ADDRESS_CREATE_URL, ADDRESS_CREATE_PAYLOAD, format="json")

        res = self.client.get(ADDRESS_LIST_URL)
        self.assertTrue(res.data["success"])
        self.assertIsNotNone(res.data["results"])

    def test_list_fail(self):
        res = self.client.get(ADDRESS_LIST_URL)
        self.assertFalse(res.data["success"])
        self.assertEqual(res.data["code"], TBResponse.CODE_4)


# class SetDefaultAddressTests(TestCaseMixin):
#     def test_set_default_success(self):
#         self.client.post(ADDRESS_CREATE_URL, ADDRESS_CREATE_PAYLOAD, format="json")
#         address_id = Address.objects.first().id
#         reverse_url = reverse("addresses:address_default", args=[address_id])
#         res = self.client.get(reverse_url)
#         self.assertTrue(res.data["success"])
#         address_from_db = Address.objects.get(pk=address_id)
#         self.assertEqual(AddressStatus.DEFAULT, address_from_db.status)
#
#     def test_set_default_fail(self):
#         reverse_url = reverse("addresses:address_default", args=[1])
#         res = self.client.get(reverse_url)
#         self.assertFalse(res.data["success"])
