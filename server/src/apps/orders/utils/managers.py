from apps.core.services.model_status import *
from apps.core.services.geo_api import GeoLocationApi, Address


class PackageManager(models.Manager, GeoLocationApi):

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


    def cancel_sub_package(self, package):
        children = package.children
        children_ids = [child.id for child in children.all()]


