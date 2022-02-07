from apps.accounts.models import UserCar
from apps.uploads.models import UploadFile, DriverLicensePhoto, CarPhoto, AddressImage, OrderImage, OrderImageType


class ImageController:
    def __init__(self, request=None):
        self.request = request
        self.user = None

    @staticmethod
    def set_address_image(address_id, image_id):
        try:
            AddressImage.objects.create(instance_id=address_id, image_id=image_id)
        except Exception as e:
            print("CREATE: AddressImage...", e.args)
            return e.args

    def set_driver_images(self, driver, images: dict):
        """
        images = {"selfie": selfie, "car_images": data["images"]["car_images"]}
        """
        self.user = driver
        try:
            if images["selfie"]:
                DriverLicensePhoto.objects.create(instance=driver, image_id=int(images["selfie"]))
                car = UserCar.objects.create(driver=driver)
                for image in images['car_images']:
                    CarPhoto.objects.create(instance=car, image_id=image['id'], type=image['type'])
        except Exception as e:
            print("CREATE: UserCar | DriverLicensePhoto | CarPhoto...", e.args)
            return e.args

    @staticmethod
    def create_order_images(images: list, order, image_type=None):
        _type = image_type if image_type else OrderImageType.BY_CUSTOMER
        if images:
            for item in images:
                OrderImage.objects.create(instance=order, image_id=int(item), type=_type)

    def find(self):
        pass

    def exists(self, images: list):
        """
        check by id: "images": [1, 2]
        check by dict: "images": [{"id": 1}]
        @return bool True / False
        """
        data = self.request
        if images:
            for file in images:
                if isinstance(file, int):
                    file_id = file
                else:
                    if "id" in file:
                        file_id = file["id"]
                    else:
                        return False, 0
                find = self.get_or_none(file_id=file_id)
                if find is None:
                    return False, file_id
            return True, None
        return True, None

    @staticmethod
    def get_or_none(file_id):
        try:
            return UploadFile.objects.get(id=file_id)
        except UploadFile.DoesNotExist:
            return None


