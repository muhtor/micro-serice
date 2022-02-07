from apps.accounts.models import UserCar
from apps.addresses.services import DataPreparer
from apps.orders.models import Order
from .mixins import *


class OrderStatusUpdateTest(TestCaseMixin):

    def register_driver(self):
        data_preparer = DataPreparer()
        order = data_preparer.create_order(OrderStatus.NEW)
        driver = data_preparer.create_driver()
        token = TBUserToken.objects.create(user=driver).key
        self.client.force_authenticate(driver, token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        return driver, order

    def test_accept(self):
        driver, order = self.register_driver()
        payload = {
            "order_id": order.order_track_id,
            "status": OrderStatus.ACCEPT,
            "qr_code": f'{order.order_track_id}12'
        }
        res = self.client.post(reverse("orders:order_status_update"), payload)
        self.assertTrue(res.data["success"])
        order_from_db = Order.objects.get(order_track_id=order.order_track_id)
        self.assertEqual(OrderStatus.ACCEPT, order_from_db.status)

        return order_from_db

    def test_accept_fail(self):
        driver, order = self.register_driver()
        payload = {
            "order_id": order.order_track_id,
            "status": OrderStatus.ACCEPT,
            "qr_code": "TBHHAJSJJ"
        }

        res = self.client.post(reverse("orders:order_status_update"), payload)
        self.assertFalse(res.data["success"])
        self.assertEqual(res.data["code"], TBResponse.CODE_44)

        payload["qr_code"] = f"{order.order_track_id}12"
        payload["status"] = OrderStatus.CANCELLED_BY_CUSTOMER
        res = self.client.post(reverse("orders:order_status_update"), payload)
        self.assertFalse(res.data["success"])
        self.assertEqual(res.data["code"], TBResponse.CODE_19)

        UserCar.objects.get(driver=driver).delete()
        payload["status"] = OrderStatus.ACCEPT
        res = self.client.post(reverse("orders:order_status_update"), payload)
        self.assertFalse(res.data["success"])
        self.assertEqual(res.data["code"], TBResponse.CODE_4)

    def test_pickup(self):
        order = self.test_accept()
        payload = {
            "order_id": order.order_track_id,
            "status": OrderStatus.PICKUP,
            "qr_code": f'{order.order_track_id}12'
        }
        res = self.client.post(reverse("orders:order_status_update"), payload)
        self.assertTrue(res.data["success"])
        order_from_db = Order.objects.get(order_track_id=order.order_track_id)
        self.assertEqual(OrderStatus.PICKUP, order_from_db.status)

        return order_from_db

    def test_pickup_fail(self):
        order = self.test_pickup()
        data_preparer = DataPreparer()
        agent = data_preparer.create_agent()
        token = TBUserToken.objects.create(user=agent).key
        self.client.force_authenticate(agent, token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        payload = {
            "order_id": order.order_track_id,
            "status": OrderStatus.DONE,
            "qr_code": f'{order.order_track_id}12'
        }
        res = self.client.post(reverse("orders:order_status_update"), payload)
        self.assertFalse(res.data["success"])
        order_from_db = Order.objects.get(order_track_id=order.order_track_id)
        self.assertEqual(OrderStatus.PICKUP, order_from_db.status)

    def test_completed_done(self):
        order = self.test_pickup()

        payload = {
            "order_id": order.order_track_id,
            "secure_code": order.secure_code,
            "image_id": None
        }
        res = self.client.post(reverse("orders:order_completed"), payload, format="json")
        self.assertTrue(res.data["success"])
        order_from_db = Order.objects.get(order_track_id=order.order_track_id)
        self.assertEqual(OrderStatus.DONE, order_from_db.status)

    def test_completed_executor_done(self):
        data_preparer = DataPreparer()
        order = self.test_pickup()

        payload = {
            "order_id": order.order_track_id,
            "secure_code": None,
            "image_id": [data_preparer.upload_file().id]
        }
        res = self.client.post(reverse("orders:order_completed"), payload, format="json")
        self.assertTrue(res.data["success"])
        order_from_db = Order.objects.get(order_track_id=order.order_track_id)
        self.assertEqual(OrderStatus.EXECUTOR_DONE, order_from_db.status)
