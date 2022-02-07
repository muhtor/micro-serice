from apps.core.services.validators import ImageController
from apps.core.services.geo_api import GeoLocationApi
from ..models import Address, AddressType, AddressStatus, WorkingDay


class AddressController(ImageController, GeoLocationApi):

    def set_address_related_objects(self, address, data: dict):
        """
        Expected data: {"images": [1, 2 ...], "working_days": [...]}
        """
        if "images" in data:
            if data["images"]:
                for image_id in data["images"]:
                    self.set_address_image(address_id=address.id, image_id=int(image_id))

        if "working_days" in data:
            working_days = data["working_days"]
            if working_days and isinstance(working_days, list):
                for day in working_days:
                    obj, _ = WorkingDay.objects.update_or_create(
                        shop_id=address.id, day=day["day"],
                        defaults={
                            "shop": address,
                            "is_working_day": day["status"],
                            "day": day["day"],
                            "work_start": day["start"],
                            "work_end": day["end"]
                        }
                    )

    @staticmethod
    def get_parcel_shop(shop_id):
        try:
            return Address.objects.get(id=shop_id)
        except Address.DoesNotExist:
            return None

    def regions_isvalid(self, data):
        if "id" in data["from"]:
            sender_city = True
        else:
            sender_city = self.find_city(city_name=data["from"]["city"])

        if "id" in data["to"]:
            receiver_city = True
        else:
            receiver_city = self.find_city(city_name=data["to"]["city"])
            # print("regions_isvalid > receiver_city........", receiver_city)

        if sender_city and receiver_city:
            return True
        else:
            return False

    def create_or_get_user_address(self, user, data):
        if "id" in data:
            address = self.get_parcel_shop(shop_id=data["id"])
        else:
            latitude = data["latitude"]
            longitude = data["longitude"]
            # address = Address.get_address(user=user, latitude=latitude, longitude=longitude, type=data["type"], phone_number=data["phone_number"])
            qs = Address.objects.filter(
                user_id=user.id, latitude=latitude, longitude=longitude,
                type=data["type"], phone_number=data["phone_number"]
            )
            print("create_or_get_user_address........", qs, type(qs))
            address = None
            if qs.exists():
                address = qs.first()
            if address is None:
                city = self.get_region(name=data["city"], coordinates=(latitude, longitude))
                kwargs = {
                    "user": user,
                    "name": data["name"],
                    "address1": data["address1"],
                    "address2": data["address2"] or "",
                    "latitude": latitude,
                    "longitude": longitude,
                    "city": city,
                    "country": user.country,
                    "type": AddressType.DOOR,
                    "full_name": data["full_name"] or "",
                    "phone_number": data["phone_number"]
                }
                try:
                    address = Address.objects.create(**kwargs)
                except Exception as e:
                    print("Exception... create_or_get_user_address 38 .. ", e.args)
                self.set_address_related_objects(address=address, data=data)
        return address

    def _get_merchant_address(self):
        user = self.request.user
        qs = Address.objects.filter(user=user, status=AddressStatus.DEFAULT)
        if qs.exists():
            return qs.first()
        else:
            return None

    def get_from_address(self):
        merchant_address = self._get_merchant_address()
        print(f"get_from_address > self._get_merchant_address()... -> ", merchant_address)
        destination_city = self.request.data["to"]["city"]
        # print(f"get_from_address > destination_city... -> ", destination_city)
        if merchant_address:
            qs = Address.objects.filter(service_city__name=destination_city, city__name__iexact=merchant_address.city.name, type=AddressType.DROP)
            if qs.filter(status=AddressStatus.REGION_DEFAULT):
                return merchant_address
            elif qs.filter(status=AddressStatus.DEFAULT):
                qs.update(status=AddressStatus.REGION_DEFAULT)
            return merchant_address
        else:
            return None


