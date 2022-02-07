from django.db.models import Sum
from apps.core.services.model_status import *
from .generators import generate_number
from apps.core.services.validators import ImageController
from apps.core.services.messenger import MessageController
from apps.core.services.geo_api import GeoLocationApi
from ..models import Order, ParcelSize, TBConfiguration


class PackageLimitController:

    @staticmethod
    def get_package_count_limit():
        """Return count limit if found `5` otherwise"""
        count_limit = TBConfiguration.get_config(key="package_order_count_limit", if_not_found=5)
        return int(count_limit)

    @staticmethod
    def get_package_weight_limit():
        """Return weight limit if found `30` otherwise"""
        weight_limit = TBConfiguration.get_config(key="package_order_weight_limit", if_not_found=30)
        return int(weight_limit)

    @staticmethod
    def get_package_dimension_limit():
        """Return dimension limit if found `90` otherwise"""
        dimension_limit = TBConfiguration.get_config(key="package_order_dimension_limit", if_not_found=90)
        return int(dimension_limit)

    @staticmethod
    def __package_dimension(package):
        """
        Private function
        Return associative array if children exists.
        [] otherwise
        """
        dimensions = []
        for order in package.children.all():
            listed = [order.order_size.width, order.order_size.height, order.order_size.length]
            dimensions.append(listed)
        return dimensions

    def calculate_package_dimensions(self, package):
        """
         Calculate package size dimension
         return `True` if it is larger than the limited size `False` otherwise
        """
        array = self.__package_dimension(package=package)
        dimensions = [sorted(item) for item in array]
        # print("sorted....", dimensions)
        height = 0  # bo'yi
        width = 0  # eni
        thickness = 0  # qalinligi
        for dimension in dimensions:
            if dimension[1] > width:
                width = dimension[1]
            if dimension[2] > height:
                height = dimension[2]
            thickness += dimension[0]
        longest = max(height, width, thickness)
        # print("LONGEST > calculate_package_dimensions...", longest, type(longest))
        if int(longest) > self.get_package_dimension_limit():
            return True
        else:
            return False

    def is_limited_over(self, package, new_order):
        """
        Main function for check package limit.
        return `True` if package size larger limited size `False` otherwise"""
        children = package.children
        if children.count() > 1:
            weight = package.children.aggregate(package_weight=Sum('order_size__weight'))
            total_weight = float(weight["package_weight"]) + float(new_order.order_size.weight)
            dimension_size = self.calculate_package_dimensions(package=package)
            if total_weight > self.get_package_weight_limit() or dimension_size:
                return True
            else:
                return False
        else:
            return False


class PackageController(MessageController, ImageController, GeoLocationApi, PackageLimitController):
    radius = 5  # km

    @staticmethod
    def calculate_duration_time(distance):
        speed = 30
        time = distance / speed
        return round(time, 2)

    def calculate_distance(self, departure, destination):
        """return distance and duration"""
        distance = self.calculate_distance_by_locations(from_location=departure, to_location=destination)
        if distance:
            duration = self.calculate_duration_time(distance=distance)
            return round(distance, 2), duration
        else:
            return float(0.0), float(0.0)

    def create_new_bundle(self, children, agent_id):
        country = self.get_country()
        order = children.last()
        bundle_code = children.last().order_track_id[7:11]
        try:
            bundle = Order.objects.create(
                country_id=country.id,
                sender_address_id=order.sender_address_id,
                receiver_address_id=order.receiver_address_id,
                driver_pickup_address_id=agent_id,
                driver_drop_address=order.receiver_address,
                urgency=DeliveryType.STANDARD,
                order_track_id=bundle_code
            )
            weights = []
            for item in children:
                weights.append(item.order_size.weight)
                bundle.children.add(item.id)

            distance, duration = self.calculate_distance(
                departure={
                    "latitude": bundle.driver_drop_address.latitude, "longitude": bundle.driver_drop_address.longitude},
                destination={
                    "latitude": bundle.receiver_address.latitude, "longitude": bundle.receiver_address.longitude}
            )
            dimensions = bundle.calculate_package_dimensions()
            bundle_size, _ = ParcelSize.objects.get_or_create(
                weight=round(sum(weights), 2), width=dimensions[0], height=dimensions[1], length=dimensions[2])
            bundle.status = OrderStatus.NEW
            bundle.distance = distance
            bundle.duration = duration
            bundle.order_size = bundle_size
            bundle.save()
            return bundle
        except Exception as e:
            print("Exception ... create_new_bundle", e.args)
            return e.args

    def create_new_package(self, order):
        country = self.get_country()
        service_agent_address = order.get_region_service_agent()
        if service_agent_address:
            service_address = service_agent_address
        else:
            service_address =  order.receiver_address
        distance, duration = self.calculate_distance(
            departure={"latitude": order.sender_address.latitude, "longitude": order.sender_address.longitude},
            destination={"latitude": service_address.latitude, "longitude": service_address.longitude}
        )
        if order.sender_address:
            title = order.sender_address.name
        else:
            title = "???"
        package_name = f"{title}-{generate_number(count=3)}"
        try:
            package = Order.objects.create()
            return package
        except Exception as e:
            print("Exception ... create_new_package", e.args)
            return e.args

    def get_package_by_radius(self, new_order):
        matches_package = None
        try:
            packages = Order.objects.filter(
                customer__isnull=True, status=OrderStatus.DRAFT,
                sender_address_id=new_order.sender_address.id,
                receiver_address__city__name__icontains=new_order.receiver_address.city.name,
            )
            if packages.exists():
                order_coordinates = (new_order.receiver_address.latitude, new_order.receiver_address.longitude)
                distances = []
                for package in packages:
                    package_coordinates = (package.receiver_address.latitude, package.receiver_address.longitude)
                    distance = Order.get_distance(point_a=package_coordinates, point_b=order_coordinates)
                    distances.append({"id": package.id, "km": distance})
                min_distance = min(distances, key=lambda x: x["km"])
                print("min_distance.......", min_distance)
                if min_distance['km'] < self.radius:
                    matches_package = Order.objects.get(id=min_distance['id'])
                print("DISTANCES.......", distances)
                print("closest_order.......", matches_package)
            if matches_package is None and packages.count() > 0:
                self.__update_track_id(order=new_order)
            return matches_package
        except Exception as e:
            print("get_package_by_radius.......", e.args)
            return None

    def __update_track_id(self, order):
        print("__update_track_id.....", order.id)
        new_bundle_code = Order.objects.get_bundle_code(to_city=order.receiver_address.city.name)
        old_track = str(order.order_track_id).split("-")
        print("old_track..", old_track)
        new_track = f"TB-{old_track[1]}-{new_bundle_code}-{old_track[3]}"
        print("new_track..", new_track)
        order.order_track_id = new_track
        order.save(update_fields=["order_track_id"])


    def create_or_nearest_package(self, order):
        package = self.get_package_by_radius(new_order=order)
        if package:
            if self.is_limited_over(package=package, new_order=order):
                self.__update_track_id(order=order)
                nearest_package = self.create_new_package(order=order)
            else:
                # Old package matches
                nearest_package = package
        else:
            # self.__update_track_id(order=order)
            nearest_package = self.create_new_package(order=order)
        return nearest_package

    def add_to_package(self, order):
        print("ADD_TO_PACKAGE...new order", order, type(order))
        package = self.create_or_nearest_package(order=order)
        print("ADD_TO_PACKAGE > package...", package, type(package))
        children = package.children.all()
        print("ADD_TO_PACKAGE > children......", children, type(children))
        # if order.id not in [child.id for child in children]:
        package.children.add(order.id)
        if package.children.count() == self.get_package_count_limit():
            package.status = OrderStatus.NEW
            package.save(update_fields=["status"])

    def cancellation_order_by_driver(self, package, car):
        initiator = package.executor
        if package.order_is_package():
            for order in package.children.all():
                print("each order.....", order, type(order))
                self.canceled_by_driver(order=order, initiator=initiator, car=car)
            package.expiry_pick_up_time = None
            package.status = OrderStatus.NEW
            package.executor = None
            package.save()
        else:
            self.canceled_by_driver(order=package,  initiator=initiator, car=car)

    def canceled_by_driver(self, order, initiator, car):
        print(f"canceled_by_driver.....{order} Driver: {initiator}")
        order.status = OrderStatus.CANCELLED_BY_EXECUTOR
        order.expiry_pick_up_time = None
        order.executor = None
        order.save()
        order.record_order_log(initiator=initiator, car=car, comment="Haydovchi tomonidan bekor qilindi")
        order.status = OrderStatus.NEW  # re modified order status to NEW
        order.save()
        self.notifying_single(user=order.customer, key=TBMessagesType.NTF_ORDER_CANCELLED_BY_DRIVER_CUSTOMER)
