from apps.core.services.price_calculator import CalculatePrice, Calculator
from apps.core.services.model_status import *
from .package import PackageController
from apps.core.services.geo_api import GeoLocationApi
from ..models import Order, ParcelSize
from .payment import PaymentController
from apps.addresses.models import Address
from apps.core.services.generics import TBResponse


class OrderController(PackageController, CalculatePrice, Calculator, GeoLocationApi, PaymentController):

    def driver_has_permission(self, executor_id):
        """Return True if the requested driver is allowed, False otherwise."""
        user = self.request.user
        if user.id == executor_id:
            return True
        else:
            return False

    def agent_has_permission(self, agent_id):
        """Return True if the requested agent is allowed, False otherwise."""
        user = self.request.user
        if user.id == agent_id:
            return True
        else:
            return False

    def merchant_order_exists(self, merchant_order_id):
        """Return True if the is already created, False otherwise."""
        user = self.request.user
        qs = Order.objects.filter(description=merchant_order_id)
        print("qs.........", qs)
        if user.type == UserType.MERCHANT and qs.exists():
            return qs.last()
        else:
            return False

    def validate_package(self, car):
        """code -> int, items -> list, msg -> dict"""
        data = self.request.data
        ids = data["orders"]
        package_id: str = data["package"]
        cancel_ids = data["cancel"]
        if cancel_ids:
            return self.validator_cancel(cancel_ids=cancel_ids, car=car)
        items = []
        qs = Order.objects.filter(order_track_id=package_id)
        if not qs.exists():
            # Parent not found
            code = TBResponse.CODE_4
            msg = TBResponse.MSG_32
            return code, items, msg
        else:
            print("DATA.......", data)
            if package_id.isdigit():
                # <<< Bundle: Pick up the order from the Agent's address >>>
                bundle = qs.last()
                print("Bundle: Pick up the order from the Agent's address >>>.......", bundle)
                if bundle.status != OrderStatus.ACCEPT:
                    # if not self.driver_has_permission(executor_id=bundle.executor.id):
                    code = TBResponse.CODE_19
                    msg = TBResponse.MSG_19
                    return code, items, msg

                if bundle.executor and not self.driver_has_permission(executor_id=bundle.executor.id):
                    code = TBResponse.CODE_40
                    msg = TBResponse.MSG_40
                    return code, items, msg

                children = bundle.children.all()
                children_ids = [item.order_track_id for item in children]  # check invalid item in package
                print("children_ids.......", children_ids)
                for track_id in children_ids:
                    if track_id not in ids:
                        items.append(track_id)

                if items:
                    # Items does not match
                    code = TBResponse.CODE_45
                    msg = TBResponse.MSG_45
                    return code, items, msg
                # success OK
                self.accept_pickup_package(package=bundle)
                code = TBResponse.CODE_0
                return code, items, {}
            else:
                # <<< Package: Pick up the order from the Merchant's address >>>
                package = qs.last()
                if package.status == OrderStatus.ACCEPT:
                    if not self.driver_has_permission(executor_id=package.executor.id):
                        code = TBResponse.CODE_40
                        msg = TBResponse.MSG_40
                        return code, items, msg

                children = package.children.all()
                children_ids = [item.order_track_id for item in children]  # check invalid item in package
                for track_id in children_ids:
                    if track_id not in ids:
                        items.append(track_id)
                print("children_ids.......", children_ids, items)
                if items:
                    # Items does not match
                    code = TBResponse.CODE_45
                    msg = TBResponse.MSG_45
                    return code, items, msg

                orders = Order.objects.filter(order_track_id__in=ids)
                if orders.exists():
                    # success OK
                    self.accept_pickup_children(car=car, orders=orders)
                    code = TBResponse.CODE_0
                    return code, items, {}

    def accept_pickup_package(self, package: Order):
        """Accept or Pickup [package, bundle]"""
        print("package > orders........", package, type(package))
        user = self.request.user
        if package.status == OrderStatus.NEW:
            package.status = OrderStatus.ACCEPT
            package.executor = user
            package.save()

            package.status = OrderStatus.PICKUP
            package.save()
        else:
            package.status = OrderStatus.PICKUP
            package.save()

        if package.order_track_id.isdigit():
            print("PACKAGE...", package.order_track_id, package.children.all())
            for order in package.children.all():
                order.executor = user
                order.save()


    def accept_pickup_children(self, car, orders):
        print("children > orders........", orders, type(orders))
        for order in orders:
            self.__accept_or_pickup_children(order=order, car=car)

    def validator_scanner(self, ids):
        """code -> int, items -> list, msg -> dict"""
        items = []
        delivery_types = []
        for track_id in ids:
            qs = Order.objects.filter(order_track_id=track_id)
            if qs.exists():
                order = qs.first()
                delivery_types.append(order.urgency)
            else:
                items.append(track_id)

        if items:
            # Orders not found
            code = TBResponse.CODE_4
            msg = TBResponse.MSG_32
            return code, items, msg

        if not self.all_equal(iterable=delivery_types):
            # Orders type not identically
            code = TBResponse.CODE_42
            msg = TBResponse.MSG_42
            return code, items, msg

        qs = Order.objects.filter(order_track_id__in=ids)
        all_merchant_ids = [order.customer_id for order in qs]  # Are the orders current merchants?
        print("ALL......", all_merchant_ids)
        if all_merchant_ids and self.all_equal(iterable=all_merchant_ids):
            merchant = qs.first().customer
            urgency = qs.first().urgency
            allowed_sts = [OrderStatus.NEW, OrderStatus.ACCEPT]
            merchant_orders = Order.objects.filter(
                customer_id=merchant.id,
                status__in=[OrderStatus.NEW, OrderStatus.ACCEPT, OrderStatus.PICKUP],
                parent__status__in=allowed_sts, urgency=urgency
            )
            print("merchant_orders........", merchant_orders)
            for merchant_order in merchant_orders:
                is_to_city = merchant_order.sender_address.city.name != merchant_order.receiver_address.city.name
                if is_to_city and merchant_order.order_track_id not in ids:
                    items.append(merchant_order.order_track_id)
            if items:
                # Items does not match
                code = TBResponse.CODE_45
                msg = TBResponse.MSG_45
                return code, items, msg
            else:
                # success OK
                code = TBResponse.CODE_0
                return code, items, {}
        else:
            # Merchant does not match
            code = TBResponse.CODE_24
            return code, items, {}

    def validator_cancel(self, cancel_ids, car):
        """code -> int, items -> list, msg -> dict"""
        items = []
        for track_id in cancel_ids:
            qs = Order.objects.filter(order_track_id=track_id, status=OrderStatus.NEW)
            if not qs.exists():
                items.append(track_id)
        if items:
            # Orders not found
            code = TBResponse.CODE_4
            msg = TBResponse.MSG_32
            return code, items, msg
        cancel_qs = Order.objects.filter(order_track_id__in=cancel_ids, status=OrderStatus.NEW)
        if cancel_qs.exists():
            all_merchant_ids = [order.customer_id for order in cancel_qs]  # Are the orders current merchants?
            if all_merchant_ids and self.all_equal(iterable=all_merchant_ids):
                print("Cancel qs........", cancel_qs)
                for order in cancel_qs:
                    self.remove_children(order=order)

                self.accept_or_pickup_order(car=car)
                # success OK
                code = TBResponse.CODE_0
                return code, items, {}
            else:
                # Merchant does not match
                code = TBResponse.CODE_24
                return code, items, {}
        else:
            # Orders not found
            code = TBResponse.CODE_4
            items = cancel_ids
            msg = TBResponse.MSG_32
            return code, items, msg

    def remove_children(self, order):
        ids = self.request.data["orders"]
        package = order.parent.last()
        package_track_ids = [item.order_track_id for item in package.children.all()]
        print("****************************************", package_track_ids)
        print(f"Cancel per PACKAGE....\n{package} \nCount: {package.children.count()}\nChild: {package.children.all()}")
        print("****************************************")
        for order_track_id in package_track_ids:
            if order_track_id in ids:
                print("CANCELLED..........................", order_track_id)
                if package.children.count() > 1:
                    package.children.remove(order.id)
                    order.executor = None
                    order.save()
                    self.add_to_package(order=order)

    def accept_or_pickup_order(self, car):
        orders_ids = self.request.data["orders"]
        for order in Order.objects.filter(order_track_id__in=orders_ids):
            self.__accept_or_pickup_children(order=order, car=car)

    def __accept_or_pickup_children(self, order, car):
        """For child order"""
        user = self.request.user
        if order.status == OrderStatus.NEW:
            order.status = OrderStatus.ACCEPT
            order.executor = user
            order.save()
            order.record_order_log(initiator=user, car=car, comment="Haydovchi tomonidan qabul qilindi")

            order.status = OrderStatus.PICKUP
            order.save()
            order.record_order_log(initiator=user, car=car, comment="Haydovchi tomonidan olib ketildi")
        else:
            order.status = OrderStatus.PICKUP
            order.save()
            order.record_order_log(initiator=user, car=car, comment="Haydovchi tomonidan olib ketildi")

    def validator_receiver(self, agent_address: Address):
        """code -> int, items -> list, msg -> dict"""
        track_ids = self.request.data["orders"]
        items = []
        package_ids = set()
        print(f"track_ids.....{track_ids} / Agent code: {agent_address.agent_code}" )
        for track_id in track_ids:
            if track_id[3:6] != str(agent_address.agent_code):
                # Address permission
                items.append(track_id)
                code = TBResponse.CODE_41
                msg = TBResponse.MSG_41
                return code, items, msg

            qs = Order.objects.filter(order_track_id=track_id)
            if qs.exists():
                parent = qs.first().parent.first()
                package_ids.add(parent.id)
            else:
                items.append(track_id)

        if items:
            # Orders not found
            code = TBResponse.CODE_4
            msg = TBResponse.MSG_32
            return code, items, msg

        order_track_ids = set()
        service_ids = []
        print("package_ids....", package_ids, type(package_ids))
        if package_ids:
            # Validate children and Receipt package
            for package_id in package_ids:
                package = Order.objects.get(id=package_id)
                service_ids.append(package.driver_drop_address.id)
                for order in package.children.all():
                    order_track_ids.add(order.order_track_id)

            # check is all item in package exists
            for order_track_id in order_track_ids:
                if order_track_id not in track_ids:
                    items.append(order_track_id)

            if items:
                # Expected order(s) not exists
                code = TBResponse.CODE_46
                msg = TBResponse.MSG_46
                return code, items, msg

            if service_ids and self.all_equal(iterable=service_ids):  # Are the orders current agent?
                agent_address_id = service_ids[0]
                print("service_ids....", service_ids, type(service_ids))
                if agent_address.id != agent_address_id:
                    # Address permission
                    code = TBResponse.CODE_41
                    return code, items, {}
                for package_id in package_ids:
                    package = Order.objects.get(id=package_id)
                    package.status = OrderStatus.DONE
                    package.save(update_fields=["status"])
                    self.create_new_bundle(children=package.children.all(), agent_id=agent_address.id)
                    # success OK
                    code = TBResponse.CODE_0
                    return code, items, {}
            else:
                # Agent does not match
                code = TBResponse.CODE_24
                return code, items, {}
        else:
            # Orders not found
            code = TBResponse.CODE_4
            msg = TBResponse.MSG_32
            return code, items, msg

        if items:
            # Orders not found
            code = TBResponse.CODE_4
            msg = TBResponse.MSG_32
            return code, items, msg

    # ********* ----- END ----- **********

    def address_is_identically(self):
        sender = self.request.data["from"]
        receiver = self.request.data["to"]
        if "id" not in sender and "id" not in receiver:
            if (sender["latitude"], sender["longitude"]) == (receiver["latitude"], receiver["longitude"]):
                return True
            else:
                return False
        elif "id" in sender and "id" in receiver:
            if int(sender["id"]) == int(receiver["id"]):
                return True
            else:
                return False
        else:
            return False

    def address_exists(self):
        data = self.request.data
        if "id" in data["from"]:
            try:
                Address.objects.get(id=data["from"]["id"], type=data["from"]["type"])
            except Address.DoesNotExist:
                invalid_id = data["from"]['id']
                return False, invalid_id
        if "id" in data["to"]:
            try:
                Address.objects.get(id=data["to"]["id"], type=data["to"]["type"])
            except Address.DoesNotExist:
                invalid_id = data["to"]['id']
                return False, invalid_id
        return True, 0

    def check_receiver_contacts(self):
        data = self.request.data
        try:
            sender_name = data["sender_name"]
            sender_phone = data["sender_phone"]
            receiver_name = data["receiver_name"]
            receiver_phone = data["receiver_phone"]
            return {
                "sender_name": sender_name or "", "sender_phone": sender_phone or "",
                "receiver_name": receiver_name or "", "receiver_phone": receiver_phone or ""}
        except Exception as e:
            print("Exception check_receiver_contacts.......", e.args)
            return {"sender_name": "", "sender_phone": "", "receiver_name": "", "receiver_phone": ""}

    @staticmethod
    def get_cities(data) -> tuple:
        from_city_name = None
        to_city_name = None
        if "city" in data["from"]:
            from_city_name = data["from"]["city"]
        else:
            qs = Address.objects.filter(id=data["from"]["id"])
            if qs.exists():
                from_city_name = qs.last().city.name

        if "city" in data["to"]:
            to_city_name = data["to"]["city"]
        else:
            qs = Address.objects.filter(id=data["to"]["id"])
            if qs.exists():
                to_city_name = qs.last().city.name
        return from_city_name, to_city_name

    def get_new_prices(self, data, user):
        from_city_name, to_city_name = self.get_cities(data)
        print(from_city_name, to_city_name)
        is_express = False
        order_price = 0
        driver_fee = 0
        dimensions = [float(data["parcel_size"]["height"]), float(data["parcel_size"]["width"]),
                      float(data["parcel_size"]["length"])]
        weight = float(data["parcel_size"]["weight"])
        delivery_type = data["delivery_option"]
        if delivery_type == DeliveryType.EXPRESS:
            is_express = True
        # if self.find_city(from_city_name) == self.find_city(to_city_name):
        #     return some_other_function_to_calculate_in_city_pricing
        zone = self.get_zone(from_city_name=from_city_name, to_city_name=to_city_name)
        parameters = self.get_right_pricing_params_for_user(user=user)
        cargo_parameters = self.get_cargo_pricing_params(user=user, type=2)
        order_price = self.calculate_interzone_price(
            parameters=parameters, cargo_params=cargo_parameters, weight=weight, is_express=is_express,
            dimensions=dimensions, zone=zone
        )
        return True, order_price

    def get_prices(self, data, user):
        from_city_name, to_city_name = self.get_cities(data)
        zone = self.get_zone(from_city_name=from_city_name, to_city_name=to_city_name)
        is_express = False
        order_price = 0
        driver_fee = 0
        dimensions = [float(data["parcel_size"]["height"]), float(data["parcel_size"]["width"]),
                      float(data["parcel_size"]["length"])]
        weights = float(data["parcel_size"]["weight"])
        delivery_type = data["delivery_option"]
        if delivery_type == DeliveryType.EXPRESS:
            is_express = True
        customer_type = "Private"
        if user.is_anonymous or user.type == UserType.CUSTOMER:
            order_price = self.calculate_price( 
                customer_type=customer_type, order_weights=[weights], dimensions=dimensions, is_express=is_express,
                home_pickup=True, zone=zone
            )
            driver_fee = self.calculate_driver_fee(number_of_orders=1, total_weight=weights, zone=zone,
                                                   origin_distances=[], destination_distances=[])
            tb_fee = order_price - driver_fee
            return True, order_price, driver_fee, tb_fee
        else:
            groups = self.get_user_role(user=user)
            for group in groups:
                if group["role"] == "Premium Merchant":
                    customer_type = "Premium"
                    break
                elif group["role"] == "Merchant":
                    customer_type = "Super"
            order_price = self.calculate_price(
                customer_type=customer_type, order_weights=[weights], dimensions=dimensions, is_express=is_express,
                home_pickup=True, zone=zone
            )
            driver_fee = self.calculate_driver_fee(number_of_orders=1, total_weight=weights, zone=zone,
                                                   origin_distances=[], destination_distances=[])
            tb_fee = order_price - driver_fee
            return True, order_price, driver_fee, tb_fee
        # return False, None, None, None

    def calculate_order_fee(self, data):
        prices = self.get_price(data)
        # prices = self.get_prices(data, user)
        print("Calculate Price -> calculate_order_fee", prices)
        if prices["found"]:
            return True, prices["estimated_price"], prices["agent_fee"], prices["driver_fee"]
        else:
            return False, None, None, None

    def create_order_size(self):
        try:
            parameters = self.request.data['parcel_size']
            weight = parameters.get('weight')
            width = parameters.get('width')
            height = parameters.get('height')
            length = parameters.get('length')
            size, _ = ParcelSize.objects.get_or_create(
                weight=weight,
                width=width,
                height=height,
                length=length,
                defaults={"weight": weight, "width": width, "height": height, "length": length}
            )
            return True, size
        except Exception as e:
            print("Exception create_order_size...", e.args)
            return False, e.args

    def perform_payment(self, data, order):
        paid_order = self.control_order_status(order=order, data=data)
        print("paid_order...", paid_order)
        if paid_order:
            is_pay_allowed = paid_order.payment_status != PaymentType.NOT_PAID
            status_is_new = paid_order.status == OrderStatus.NEW
            # is_with_agent = order.order_track_id[3:6] != "000"
            if paid_order.urgency == DeliveryType.STANDARD and is_pay_allowed and status_is_new:
                self.add_to_package(order=order)
            return True
        else:
            return False

try:
    pass
    # from django.db.models import F
    # qs = Order.objects.filter(sender_address__city__name=F('receiver_address__city__name'))
    # print("QS.......", qs, type(qs))

    # order_ids = ["TB-002-5776-348", "TB-002-5776-566", "TB-002-5776-762"]
    # qs = Order.objects.filter(customer__isnull=True)
    # required = []
    # parents = set()
    # for item in qs:
    #     child = item.children.all()
    #     print("p.......", child)
    # print("Item....", required, type(required))

    # # print(f"64.........{package, type(package)} -- {new_order, type(new_order)}")
    # weight = package.children.aggregate(package_weight=Sum('order_size__weight'))
    # print(f"WEIGHT.......{weight} -- {new_order.order_size.weight, type(new_order.order_size.weight)}")
    # print("W......", weight, type(weight))
    # print("C.....", sos, type(sos))
    # item = Order.objects.get(id=6)
    # new_package = item.parent.filter(status=OrderStatus.NEW)
    # if new_package.exists() and new_package.first().children.exists():
    #     child = new_package.first().children.all()
    #     print("1.....", child, type(child))
    # qs = Address.objects.filter(
    #     service_city=order.receiver_address.city, city=order.sender_address.city, status=AddressStatus.REGION_DEFAULT
    # )
    # new = Order.manager.create_sub_package(package=order)
    # parent = order.parent.exists()
    # children = parent.children.all()
    # package = order.parent.last()
    # orders = Order.objects.prefetch_related('parent__children')
    # orders = order.parent.filter(status=OrderStatus.NEW).prefetch_related('parent')
    # orders = Order.objects.filter(status=OrderStatus.NEW, customer__isnull=False).prefetch_related(Prefetch('parent'))

    # accept = order.parent.filter(status=OrderStatus.ACCEPT)
    # print("1.....", orders, type(orders))
    # print("1.....", new, type(new))
    # print("2.....", accept, type(accept))
    # print("2.....", accept, type(accept))
    # child = package.children.remove(order.id)
    # print("2.....", package, type(package))
    # print("3.....", child, type(child))
    # print("Child.....", children, type(children))
#     package = order.parent.all()
#     print("2.....", package, type(package))

#     package = Order.objects.get(id=134)
#     children = package.children.all()
#     print("C......", children, type(children))
#     if order.id not in [child.id for child in children.all()]:
#         print("2......", [child.id for child in children.all()], type([child.id for child in children.all()]))
#         package.children.add(order.id)
#     else:
#         print("COUNT....", children.count())
#         if children.count() == 5:
#             print("3......", [child.id for child in children.all()], type([child.id for child in children.all()]))
#         else:
#             print("4......", [child.id for child in children.all()], type([child.id for child in children.all()]))
#
except Exception as e:
    print("Exception.......", e.args)

# try:
#     import base64
#     order = Order.objects.get(order_track_id="TBVH5375")
#     amount = int(order.amount) * 100
#     paycom_url = "https://checkout.paycom.uz/"
#     # paycom_url = "https://test.paycom.uz/"
#     params = f"m=61bb0a32204c85a50a88c8c1;ac.order_id={order.order_track_id};a={amount}"
#     encoded_param = base64.b64encode(bytes(params, "utf-8")).decode('ascii')
#     data = f"{paycom_url}{encoded_param}"
#     print("D.......", data)
# except Exception as e:
#     print("E,........", e.args)


