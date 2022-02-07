from itertools import groupby
from geopy.distance import geodesic, great_circle
from reverse_geocoder import search
from apps.core.services.model_status import AddressStatus, AddressType
from django.db.models.expressions import RawSQL
from ...addresses.models import Country, City, TBZone, Address


class TBZoneController:
    # Regions
    TASHKENT = 'Tashkent'
    NAMANGAN = 'Namangan'
    ANDIJAN = 'Andijan'
    FERGHANA = 'Fergana'
    SIRDARYO = 'Syrdarya'
    JIZZAKH = 'Djizzak'
    SAMARQAND = 'Samarkand'
    BUKHARA = 'Bukhara'
    NAVOIY = 'Navoiy'
    QASHQADARYO = 'Kashkadarya'
    SURXONDARYO = 'Surkhandarya'
    XORAZM = 'Khorezm'
    KARAKALPAKSTAN = 'Republic of Karakalpakstan'

    REGIONS = {
        'TOS': TASHKENT,
        'TO': TASHKENT,
        'TK': TASHKENT,
        'TAS': TASHKENT,

        'NAM': NAMANGAN,
        'NG': NAMANGAN,

        'AND': ANDIJAN,
        'AN': ANDIJAN,

        'FER': FERGHANA,
        'FAR': FERGHANA,
        'FA': FERGHANA,

        'SI': SIRDARYO,
        'SIR': SIRDARYO,
        'SYR': SIRDARYO,

        'JIZ': JIZZAKH,
        'JI': JIZZAKH,
        'DJI': JIZZAKH,

        'SAM': SAMARQAND,
        'SA': SAMARQAND,

        'BUK': BUKHARA,
        'BU': BUKHARA,

        'NAV': NAVOIY,
        'NW': NAVOIY,

        'KAS': QASHQADARYO,
        'QAS': QASHQADARYO,
        'QA': QASHQADARYO,

        'SUR': SURXONDARYO,
        'SU': SURXONDARYO,

        'KHO': XORAZM,
        'XO': XORAZM,
        'XOR': XORAZM,

        'KAR': KARAKALPAKSTAN,
        'QR': KARAKALPAKSTAN,
        'REP': KARAKALPAKSTAN,
    }

    def get_city_by_prefix(self, region_name):
        return self.REGIONS.get(region_name[:3].upper(), None)


class GeoAdministration(TBZoneController):
    def __init__(self):
        self.TB_ZONES = {
            f"{self.TASHKENT}|{self.TASHKENT}": 0,
            f"{self.TASHKENT}|{self.NAMANGAN}": 1,
            f"{self.TASHKENT}|{self.ANDIJAN}": 1,
            f"{self.TASHKENT}|{self.FERGHANA}": 1,
            f"{self.TASHKENT}|{self.SIRDARYO}": 1,
            f"{self.TASHKENT}|{self.JIZZAKH}": 1,
            f"{self.TASHKENT}|{self.SAMARQAND}": 1,
            f"{self.TASHKENT}|{self.BUKHARA}": 2,
            f"{self.TASHKENT}|{self.NAVOIY}": 2,
            f"{self.TASHKENT}|{self.QASHQADARYO}": 2,
            f"{self.TASHKENT}|{self.SURXONDARYO}": 3,
            f"{self.TASHKENT}|{self.XORAZM}": 4,
            f"{self.TASHKENT}|{self.KARAKALPAKSTAN}": 5,

            f"{self.NAMANGAN}|{self.NAMANGAN}": 0,
            f"{self.NAMANGAN}|{self.TASHKENT}": 1,
            f"{self.NAMANGAN}|{self.ANDIJAN}": 1,
            f"{self.NAMANGAN}|{self.FERGHANA}": 1,
            f"{self.NAMANGAN}|{self.SIRDARYO}": 1,
            f"{self.NAMANGAN}|{self.JIZZAKH}": 1,
            f"{self.NAMANGAN}|{self.SAMARQAND}": 1,
            f"{self.NAMANGAN}|{self.BUKHARA}": 2,
            f"{self.NAMANGAN}|{self.NAVOIY}": 2,
            f"{self.NAMANGAN}|{self.QASHQADARYO}": 2,
            f"{self.NAMANGAN}|{self.SURXONDARYO}": 3,
            f"{self.NAMANGAN}|{self.XORAZM}": 4,
            f"{self.NAMANGAN}|{self.KARAKALPAKSTAN}": 5,
        }

    COUNTRIES = {
        "+7": {"name": "Russia", "currency": "RUB"},
        "+90": {"name": "Turkey", "currency": "TRY"},
        "+993": {"name": "Turkmenistan", "currency": "TKM"},
        "+996": {"name": "Kyrgyzstan", "currency": "KGS"},
        "+998": {"name": "Uzbekistan", "currency": "UZS"}
    }

    def get_region_zone(self, city_a: str, city_b: str):
        from_city = self.get_city_by_prefix(region_name=city_a)
        to_city = self.get_city_by_prefix(region_name=city_b)
        key_str = "|".join([from_city, to_city])
        zone = self.TB_ZONES[key_str]
        return zone

    GEO_API_CITY = {
        'Tashkent': 1,
        'Toshkent': 1,
        'Toshkent Shahri': 1,
        'Namangan': 1,
        'Andijon': 1,
        'Fergana': 1,
        'Sirdaryo': 1,
        'Jizzax': 1,
        'Samarqand': 1,
        'Bukhara': 2,
        'Navoiy': 2,
        'Qashqadaryo': 2,
        'Surxondaryo': 3,
        'Xorazm': 4,
        'Karakalpakstan': 5
    }


class GeoLocationApi(GeoAdministration):

    @classmethod
    def all_equal(cls, iterable):
        "Returns `True` if all the elements are equal to each other, `False` otherwise"
        g = groupby(iterable)
        return next(g, True) and not next(g, False)

    @staticmethod
    def get_user_role(user) -> list:
        groups = user.groups.all()
        result = []
        if groups.exists():
            for role in groups:
                result.append({"role": role.name})
        return result

    @staticmethod
    def parse_city(data):
        if "city" in data["from"]:
            from_city_name = data["from"]["city"]
        else:
            qs = Address.objects.filter(id=data["from"]["id"])
            if qs.exists():
                from_city_name = qs.last().city.name
            else:
                from_city_name = None

        if "city" in data["to"]:
            to_city_name = data["to"]["city"]
        else:
            qs = Address.objects.filter(id=data["to"]["id"])
            if qs.exists():
                to_city_name = qs.last().city.name
            else:
                to_city_name = None
        return from_city_name, to_city_name

    @staticmethod
    def country_query(data):
        obj, _ = Country.objects.get_or_create(name=data['name'], currency=data['currency'])
        return obj

    def get_country(self, prefix=None):
        data = {"name": "Uzbekistan", "currency": "UZS"}
        if prefix == '+998':
            country_info = self.COUNTRIES.get(prefix) or data
            return self.country_query(data=country_info)
        else:
            return self.country_query(data=data)

    def default_coordinate(self, region_name: str):
        """Return `region default coordinates` -> ex. (41.123456, 71.123456)"""
        region = self.REGIONS.get(region_name[:3].upper(), None)
        if region:
            coordinates = {
                'Tashkent': (41.311158, 69.279737),
                'Namangan': (41.000085, 71.672579),
                'Andijan': (40.783388, 72.350663),
                'Fergana': (40.389420, 71.783009),
                'Syrdarya': (40.627754, 68.788412),
                'Djizzak': (40.120288, 67.828508),
                'Samarkand': (39.654543, 66.968847),
                'Bukhara': (39.767945, 64.421701),
                'Navoiy': (40.103093, 65.373970),
                'Kashkadarya': (38.841654, 65.790015),
                'Surkhandarya': (37.229019, 67.276754),
                'Khorezm': (41.549689, 60.631377),
                'Republic of Karakalpakstan': (42.460334, 59.617987)
            }
            return coordinates.get(region, (41.123456, 71.123456))
        else:
            return (41.123456, 71.123456)

    def search_city(self, coordinates: tuple):
        """return `region administration name` by (latitude, longitude) if find, `None` otherwise."""
        region_name: str = ""
        try:
            location = search(coordinates)
            print("Location administration ... ", location)
            if location:
                region_name = location[0]["admin1"]
                region_array = region_name.split(' ')
                if len(region_array) > 1:
                    region_name = region_array[0]
                prefix = region_name.upper()[:3]
                if prefix == "TOS" or prefix == "TAS":
                    region_name = self.REGIONS.get("TAS")
                tb_region = self.get_city_by_prefix(region_name=region_name)
                if tb_region:
                    region_name = tb_region
        except Exception as e:
            print("search_city...", e.args)
        return region_name

    def find_city(self, city_name: str) -> bool:
        """Return `True` if it find, `False` otherwise."""
        if city_name[:3].upper() in self.REGIONS:
            return True
        elif city_name[:2].upper() in self.REGIONS:
            return True
        else:
            return False

    def find_region(self, region_name: str):
        """Return `region unique name` if it find, `None` otherwise."""
        city_key = region_name[:3].upper()
        return self.REGIONS.get(city_key, None)

    def get_zone(self, from_city_name: str, to_city_name: str, coordinate_a=None, coordinate_b=None) -> int:
        """Return `Zone [int, float]` by city names if find, `Search from API or CSV` otherwise."""
        from_city = self.find_region(region_name=from_city_name)
        to_city = self.find_region(region_name=to_city_name)
        if from_city and to_city:
            qs = TBZone.objects.filter(from_city__name__icontains=from_city, to_city__name__icontains=to_city)
        else:
            qs = TBZone.objects.filter(from_city__name__icontains=from_city_name, to_city__name__icontains=to_city_name)
        if qs.exists():
            zone: int = qs.first().zone
        else:
            zone: int = 1
        return 1 if zone == 0 else zone

    def get_region(self, name, coordinates: tuple):
        """Return `City object` by city name if find, `Create new` otherwise."""
        region_name = self.get_city_by_prefix(region_name=name)
        if region_name:
            city_name = region_name
        else:
            city_name = name
        qs = City.objects.filter(name__icontains=city_name)
        if qs.exists():
            city = qs.first()
        else:
            country = Country.create_country_uz()
            find = self.search_city(coordinates=coordinates)
            if find:
                city = City.objects.create(name=find, country=country)
            else:
                return False
        return city

    def calculate_distance_by_locations(self, from_location, to_location):
        """
        Measuring Distance
        > calculate coordinate: https://geopy.readthedocs.io/en/latest/#geopy.geocoders.Nominatim

            Using geodesic distance:
            -------------------------------
            from geopy.distance import geodesic
            newport_ri = (41.49008, -71.312796)
            cleveland_oh = (41.499498, -81.695391)
            geodesic(newport_ri, cleveland_oh).miles // 538.390445368
            *********************************************************
            Using great-circle distance:
            -------------------------------
            from geopy.distance import great_circle
            newport_ri = (41.49008, -71.312796)
            cleveland_oh = (41.499498, -81.695391)
            great_circle(newport_ri, cleveland_oh).miles //536.997990696
        """
        if from_location and to_location:
            # print("FROM...", from_location, type(from_location))
            # print("TO...", to_location, type(to_location))
            # distance = great_circle(_from, _to).miles
            newport_ri = (from_location['latitude'], from_location['longitude'])
            cleveland_oh = (to_location['latitude'], to_location['longitude'])
            geodesic_distance = geodesic(newport_ri, cleveland_oh).kilometers
            return geodesic_distance
        else:
            return None

    @staticmethod
    def distance_between_orders(coordinates_a: tuple, coordinates_b: tuple):
        if coordinates_a and coordinates_b:
            return geodesic(coordinates_a, coordinates_b).kilometers
        else:
            return None

    def get_locations_nearby_coords(self, latitude, longitude, max_distance=None):
        """
        ##############################################################
            SELECT id, ( 3959 * acos( cos( radians(37) ) * cos( radians( lat ) )
            * cos( radians( lng ) - radians(-122) ) + sin( radians(37) ) * sin(radians(lat)) ) ) AS distance
            FROM markers
            HAVING distance < 25 ORDER BY distance LIMIT 0 , 20;
        ##############################################################
        https://stackoverflow.com/questions/19703975/django-sort-by-distance
        Return objects sorted by distance to specified coordinates
        which distance is less than max_distance given in kilometers
        """

        # Great circle distance formula
        gcd_formula = "6371 * acos(least(greatest(cos(radians(%s)) * cos(radians(latitude)) * cos(radians(longitude) - radians(%s)) + sin(radians(%s)) * sin(radians(latitude)), -1), 1))"
        raw_sql = RawSQL(gcd_formula, (latitude, longitude, latitude))
        qs = Address.objects.filter(
            type=AddressType.DROP, status=AddressStatus.DEFAULT).annotate(distance=raw_sql).order_by('distance')
        if max_distance is not None:
            qs = qs.filter(distance__lte=max_distance)
        return qs
