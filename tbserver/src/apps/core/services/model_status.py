from django.db import models
from django.db.models import Q, F
import pytz
import pytz
from datetime import timedelta, datetime
from django.utils import timezone


class BitwiseNumber:
    BIT_1 = 1
    BIT_2 = 2
    BIT_3 = 4
    BIT_4 = 8
    BIT_5 = 16
    BIT_6 = 32
    BIT_7 = 64
    BIT_8 = 128
    BIT_9 = 256
    BIT_10 = 512
    BIT_11 = 1024
    BIT_12 = 2048
    BIT_13 = 4096
    BIT_14 = 8192
    BIT_15 = 16384
    BIT_16 = 32768
    BIT_17 = 65536


def default_value():
    return float(0.0)


class Enum(models.IntegerChoices):
    @classmethod
    def attr_list(cls):
        return list(map(lambda c: c.value, cls))

    @classmethod
    def attr_dict(cls):
        return {i.value: i.name for i in cls}

    @classmethod
    def get_attr(cls, number):
        attributes = list(map(lambda c: c.value, cls))
        for attribute in attributes:
            if attribute == number:
                return attribute
        return None


class ApplicationType(Enum):
    CUSTOMER_APP = BitwiseNumber.BIT_1  # 1
    AGENT_APP = BitwiseNumber.BIT_2  # 2
    DRIVER_APP = BitwiseNumber.BIT_3  # 4


class LanguageStatus(models.IntegerChoices):
    UZ = BitwiseNumber.BIT_1
    EN = BitwiseNumber.BIT_2
    RU = BitwiseNumber.BIT_3


class LanguageType(models.TextChoices):
    UZ = "UZ", "uz"
    EN = "EN", "en"
    RU = "RU", "ru"


class ActivationType(Enum):
    REGISTER = BitwiseNumber.BIT_1
    RESEND = BitwiseNumber.BIT_2
    FORGOT = BitwiseNumber.BIT_3
    CHANGE = BitwiseNumber.BIT_4
    LOGIN = BitwiseNumber.BIT_5
    ORDER = BitwiseNumber.BIT_6
    ORDER_TRANSFER = BitwiseNumber.BIT_7


class UserStatus(models.IntegerChoices):
    NOTACTIVATED = BitwiseNumber.BIT_1
    TOBEACTIVATED = BitwiseNumber.BIT_2
    ACTIVATED = BitwiseNumber.BIT_3
    DELETED = BitwiseNumber.BIT_4


class UserType(models.IntegerChoices):
    CUSTOMER = BitwiseNumber.BIT_1
    AGENT = BitwiseNumber.BIT_2
    DRIVER = BitwiseNumber.BIT_3
    MERCHANT = BitwiseNumber.BIT_4
    MERCHANTUSER = BitwiseNumber.BIT_5
    ADMIN = BitwiseNumber.BIT_6
    TEZBORUSER = BitwiseNumber.BIT_7
    WEBSITEUSER = BitwiseNumber.BIT_8


class UserDeviceType(Enum):
    ANDROID = BitwiseNumber.BIT_1
    IOS = BitwiseNumber.BIT_2
    WEB = BitwiseNumber.BIT_3


class NotificationSender(models.IntegerChoices):
    TEZBOR = BitwiseNumber.BIT_1
    ADMIN = BitwiseNumber.BIT_2


class NotificationStatus(models.IntegerChoices):
    SUCCESS = BitwiseNumber.BIT_1
    FAILED = BitwiseNumber.BIT_2


class NotificationType(models.IntegerChoices):
    SINGLE = BitwiseNumber.BIT_1
    MULTIPLE = BitwiseNumber.BIT_2


class TBMessagesType(models.TextChoices):
    SMS_PHONE_CONFIRMATION_TEXT_CUSTOMER = "sms_phone_confirmation_text_customer"
    SMS_PHONE_CONFIRMATION_TEXT_AGENT = "sms_phone_confirmation_text_agent"
    SMS_PHONE_CONFIRMATION_TEXT_DRIVER = "sms_phone_confirmation_text_driver"
    SMS_ORDER_CREATE_SENDER = "sms_order_create_sender"
    SMS_ORDER_CREATE_RECEIVER = "sms_order_create_receiver"
    NTF_YOUR_ORDER_ACCEPTED_CUSTOMER = "ntf_your_order_accepted_customer"
    NTF_BEFORE_EXP_ORDER_PICKUP_TIME_DRIVER = "ntf_before_exp_order_pickup_time_driver"
    NTF_EXPIRED_ORDER_PICKUP_TIME_DRIVER = "ntf_expired_order_pickup_time_driver"
    NTF_EXPIRED_ORDER_PICKUP_TIME_CUSTOMER = "ntf_expired_order_pickup_time_customer"
    NTF_ORDER_CANCELLED_BY_DRIVER_CUSTOMER = "ntf_order_cancelled_by_driver_customer"
    NTF_ORDER_IS_ON_THE_WAY_CUSTOMER = "ntf_order_is_on_the_way_customer"
    NTF_ORDER_COMPLETED_CUSTOMER = "ntf_order_completed_customer"
    NTF_ORDER_SEND_CUSTOMER = "ntf_order_send_customer"
    NTF_DRIVER_ACTIVATED_DRIVER = "ntf_driver_activated_driver"
    NTF_AGENT_ACTIVATED_AGENT = "ntf_agent_activated_agent"
    NTF_NEW_ORDER_AVAILABLE_DRIVER = "ntf_new_order_available_driver"
    NTF_BALANCE_INCREMENT_DRIVER = "ntf_balance_increment_driver"
    NTF_BALANCE_DECREMENT_DRIVER = "ntf_balance_decrement_driver"


class UserCarType(models.IntegerChoices):
    SEDAN = BitwiseNumber.BIT_1
    TRUCK = BitwiseNumber.BIT_2
    VAN = BitwiseNumber.BIT_3
    OTHER = BitwiseNumber.BIT_4


class UserCarColor(models.IntegerChoices):
    WHITE = BitwiseNumber.BIT_1
    BLACK = BitwiseNumber.BIT_2
    RED = BitwiseNumber.BIT_3
    ORANGE = BitwiseNumber.BIT_4
    YELLOW = BitwiseNumber.BIT_5
    BROWN = BitwiseNumber.BIT_6


class UserCarStatus(models.IntegerChoices):
    INACTIVE = BitwiseNumber.BIT_1
    ACTIVE = BitwiseNumber.BIT_2
    DEFAULT = BitwiseNumber.BIT_3
    DELETED = BitwiseNumber.BIT_4


class UserFilterStatus(models.IntegerChoices):
    INACTIVE = BitwiseNumber.BIT_1
    ACTIVE = BitwiseNumber.BIT_2
    DELETED = BitwiseNumber.BIT_4
    

class UserCarPhotoType(models.IntegerChoices):
    FRONT_VIEW = 1
    REAR_VIEW = 2
    RIGHT_VIEW = 3
    LEFT_VIEW = 4
    OTHER = 5


class UserLocationType(models.IntegerChoices):
    CURRENT = BitwiseNumber.BIT_1
    PAST = BitwiseNumber.BIT_2


class AddressStatus(models.IntegerChoices):
    INACTIVE = BitwiseNumber.BIT_1
    ACTIVE = BitwiseNumber.BIT_2
    DEFAULT = BitwiseNumber.BIT_3
    DELETED = BitwiseNumber.BIT_4
    REGION_DEFAULT = BitwiseNumber.BIT_5


class AddressType(models.IntegerChoices):
    DOOR = BitwiseNumber.BIT_1
    DROP = BitwiseNumber.BIT_2


class UserAccountStatus(models.IntegerChoices):
    ACTIVE = BitwiseNumber.BIT_1
    DELETED = BitwiseNumber.BIT_2


class UserAccountType(models.IntegerChoices):
    TEZBOR = BitwiseNumber.BIT_1
    UZ_CARD = BitwiseNumber.BIT_2
    HUMO_CARD = BitwiseNumber.BIT_3


class PaymentType(models.IntegerChoices):
    NOT_PAID = BitwiseNumber.BIT_1
    CASH = BitwiseNumber.BIT_2
    PAYME = BitwiseNumber.BIT_3
    VISA = BitwiseNumber.BIT_4
    TEZBOR_PAYMENT = BitwiseNumber.BIT_5
    RECEIVER_CASH = BitwiseNumber.BIT_6
    VIP_PAYMENT = BitwiseNumber.BIT_7


class TransactionType(models.IntegerChoices):
    RECEIVED_FROM_CUSTOMER = BitwiseNumber.BIT_1
    EARNED_BY_SHIPPING = BitwiseNumber.BIT_2
    EARNED_BY_STORING = BitwiseNumber.BIT_3
    DEPOSIT_BALANCE = BitwiseNumber.BIT_4
    WITHDRAW_BALANCE = BitwiseNumber.BIT_5
    RECEIVED_FROM_RECEIVER = BitwiseNumber.BIT_6
    RECEIVED_BY_REFERRING = BitwiseNumber.BIT_7
    PAID_VIP_ORDER = BitwiseNumber.BIT_8


class TransactionStatus(models.IntegerChoices):
    SUCCESS = BitwiseNumber.BIT_1
    UNSUCCESSFUL = BitwiseNumber.BIT_2


class TransactionState(models.IntegerChoices):
    STATE_CREATED = 1
    STATE_COMPLETED = 2
    STATE_CANCELLED = -1
    STATE_CANCELLED_AFTER_COMPLETE = -2
    STATE_WITHDRAW_IN_PROGRESS = 4
    STATE_WITHDRAW_COMPLETED = 5


class TariffServiceType(models.IntegerChoices):
    DROP_OFF_TO_DROP_OFF = BitwiseNumber.BIT_1
    DROP_OFF_TO_ADDRESS = BitwiseNumber.BIT_2
    ADDRESS_TO_DROP_OFF = BitwiseNumber.BIT_3
    ADDRESS_TO_ADDRESS = BitwiseNumber.BIT_4


class TariffInfoUnitType(models.IntegerChoices):
    WEIGHT = BitwiseNumber.BIT_1
    DISTANCE = BitwiseNumber.BIT_2
    MEASUREMENT = BitwiseNumber.BIT_3


class TariffServiceStatus(models.IntegerChoices):
    ACTIVE = BitwiseNumber.BIT_1
    INACTIVE = BitwiseNumber.BIT_2


class PlaceType(models.IntegerChoices):
    IN_CITY = BitwiseNumber.BIT_1
    TO_CITY = BitwiseNumber.BIT_2


class FAQStatus(models.IntegerChoices):
    ACTIVE = BitwiseNumber.BIT_1
    INACTIVE = BitwiseNumber.BIT_2


class ContentType(models.IntegerChoices):
    PRIVACY_POLICY = BitwiseNumber.BIT_1
    ABOUT = BitwiseNumber.BIT_2
    BLACKLIST = BitwiseNumber.BIT_3
    MAXIMUM_SIZE = BitwiseNumber.BIT_4


class DeliveryType(models.IntegerChoices):
    STANDARD = BitwiseNumber.BIT_1
    EXPRESS = BitwiseNumber.BIT_2


class OrderType(models.IntegerChoices):
    DELIVERY = BitwiseNumber.BIT_1
    TAXI = BitwiseNumber.BIT_2
    RENT = BitwiseNumber.BIT_3


class ParcelCategory(models.IntegerChoices):
    FRAGILE = BitwiseNumber.BIT_1
    NONFRAGILE = BitwiseNumber.BIT_2


class OrderStatus(models.IntegerChoices):
    DRAFT = BitwiseNumber.BIT_1  # 1
    EXPECTED = BitwiseNumber.BIT_2  # 2
    NEW = BitwiseNumber.BIT_3  # 4
    ACCEPT = BitwiseNumber.BIT_4  # 8
    PICKUP = BitwiseNumber.BIT_5  # 16
    EXECUTOR_DONE = BitwiseNumber.BIT_6  # 32
    AGENT_RECEIVED = BitwiseNumber.BIT_7  # 64
    CUSTOMER_DONE = BitwiseNumber.BIT_8  # 128
    DONE = BitwiseNumber.BIT_9  # 256
    CANCELLED_BY_CUSTOMER = BitwiseNumber.BIT_10  # 512
    CANCELLED_BY_EXECUTOR = BitwiseNumber.BIT_11
    DELETED = BitwiseNumber.BIT_12
    PRIOR_WAITING = BitwiseNumber.BIT_13
    NEXT_WAITING = BitwiseNumber.BIT_14
    PRE_NEW = BitwiseNumber.BIT_15
    PRE_ACCEPT = BitwiseNumber.BIT_16


class OrderRecordStatus(models.IntegerChoices):
    EXTEND_ACCEPT = BitwiseNumber.BIT_1


class OrderCashStatus(Enum):
    NOT_RECEIVED = BitwiseNumber.BIT_1
    CASH_RECEIVED = BitwiseNumber.BIT_2
    CASH_WILL_BE_RECEIVED = BitwiseNumber.BIT_3


class OrderImageType(models.IntegerChoices):
    BY_CUSTOMER = BitwiseNumber.BIT_1
    BY_AGENT = BitwiseNumber.BIT_2
    BY_DRIVER = BitwiseNumber.BIT_3


class CityZone(models.IntegerChoices):
    Zone0 = 0
    Zone1 = 1
    Zone2 = 2
    Zone3 = 3
    Zone4 = 4
    Zone5 = 5


class TriggerType(Enum):
    SHOW_PACKAGE_TO_OFFER = 1
    NOTIFY_DRIVER_EXP_ACCEPT = 2
    RETURN_TO_OFFER = 3
    REDISTRIBUTION_OF_PACKAGE = 4


class JobStatus(Enum):
    CREATED = 1
    PROGRESS = 2
    DONE = 3
    FORCE_DONE = 4
    FAILED = 5
