from apps.accounts.models import User, TBUserToken, UserDevice, TBNotificationRecord, UserFilter, TBMessages
from django.utils import translation
from django.conf import settings
from pyfcm import FCMNotification
from apps.core.services.model_status import *
from apps.core.services.decorators import message_prefixing


class TBPusher:
    def __init__(self):
        self.lang = "uz"

    @staticmethod
    def _get_application_secret_key(app_type):
        """https://apscheduler.readthedocs.io/en/"""
        keys = {
            ApplicationType.CUSTOMER_APP: settings.PYFCM_CUSTOMER_SERVER_KEY,
            ApplicationType.AGENT_APP: settings.PYFCM_AGENT_SERVER_KEY,
            ApplicationType.DRIVER_APP: settings.PYFCM_DRIVER_SERVER_KEY
        }
        return keys.get(app_type)

    def get_messages(self, key, prefix=None):
        lang = self.lang
        # print("Lang....", lang, type(lang))
        translation.activate(lang)
        msg = TBMessages.get_message(type=key)
        if msg:
            response = {"title": msg.title, "body": ""}
            if prefix:
                response["body"] = message_prefixing(str(msg.message), prefix)
            else:
                response["body"] = msg.message
            return response
        else:
            return None

    def _notify_single(self, user_token: TBUserToken, app: ApplicationType, message):
        api_key = self._get_application_secret_key(app_type=app)
        # print("PUSHER...single", api_key)
        push_service = FCMNotification(api_key=api_key)
        result = push_service.notify_single_device(
            registration_id=user_token.device_token, message_title=message["title"], message_body=message["body"])
        self._record_notifications(result=result, msg=message, user=user_token.user)

    def _notify_multiple(self, ids, message):
        api_key = self._get_application_secret_key(app_type=ApplicationType.DRIVER_APP)
        push_service = FCMNotification(api_key=api_key)
        result = push_service.notify_multiple_devices(
            registration_ids=ids, message_title=message["title"], message_body=message["body"])
        self._record_notifications(result=result, msg=message)
        return True

    def notifying_single(self, user, key, prefix=None):
        """
        user: User
        key: TBMessages type ( TBMessagesType for find msg text)
        prefix: Dynamic value
        notification_data = {"title": msg_title, "body": msg_body, "data": {"test": "test"}}
        pusher.notifying_single(message=notification_data)
        """
        qs = TBUserToken.objects.filter(user_id=user.id)
        msg_content = self.get_messages(key=key, prefix=prefix)
        # print(f"Pusher > Notify single: msg_content, {qs} -- {msg_content, type(msg_content)}")
        if qs.exists() and msg_content:
            user_token = qs.last()
            return self._notify_single(user_token=user_token, app=user.app_type, message=msg_content)
        return False

    # def notifying_multiple(self, user_type, key):
    #     qs = UserDevice.objects.filter(user__type=user_type, user__status=UserStatus.ACTIVATED)
    #     msg_content = self.get_messages(key=key)
    #     if qs.exists() and msg_content:
    #         ids = [device.registration_id for device in qs]
    #         return self._notify_multiple(ids=ids, user_type=user_type, message=msg_content)
    #     return False

    def notify_drivers_new_orders(self, order):
        """
        order: Order
        key: TBMessages type ( TBMessagesType for find msg text)
        """
        # from_city = order.sender_address.city.name
        # filtered_drivers = UserFilter.objects.filter(from_city__istartswith=from_city, status=UserFilterStatus.ACTIVE)
        msg_content = self.get_messages(key=TBMessagesType.NTF_NEW_ORDER_AVAILABLE_DRIVER)
        ids = []
        if msg_content:
            drivers = TBUserToken.objects.filter(user__type=UserType.DRIVER)
            # print(f"Pusher > Notify New order, {drivers} -- {msg_content, type(msg_content)}")
            for user in drivers:
                ids.append(user.device_token)
            # if filtered_drivers.exists():
            #     users_ids = [driver.user.id for driver in filtered_drivers]
            #     devices = UserDevice.objects.filter(user_id__in=users_ids, user__status=UserStatus.ACTIVATED)
            #     for device in devices:
            #         ids.append(device.registration_id)
            # print("REGISTRATION_ID from filter.....", ids, type(ids))
            # qs = User.objects.filter(type=UserType.DRIVER, status=UserStatus.ACTIVATED)
            # if qs.exists():
            #     new_driver = qs.exclude(user_filter__isnull=False)
            #     print("new_driver....", new_driver)
                # new_driver_ids = [user.id for user in new_driver]
                # devices = UserDevice.objects.filter(user_id__in=new_driver_ids)
                # for device in devices:
                #     ids.append(device.registration_id)
            # print("REGISTRATION_ID new users.....", ids, type(ids))
            if ids:
                return self._notify_multiple(ids=ids, message=msg_content)
        return False

    def notify_tb_users(self, message):
        qs = UserDevice.objects.filter(user__status=UserStatus.ACTIVATED)
        if qs.exists() and message:
            ids = [device.registration_id for device in qs]
            self._notify_multiple(ids=ids, message=message)
            # self._notify_multiple(ids=ids, user_type=UserType.DRIVER, message=message)
            return True
        return False

    @staticmethod
    def _record_notifications(result, msg, user=None):
        # print("Notification: RESULT...", result, type(result))
        if "success" in result:
            status = NotificationStatus.SUCCESS if result["success"] else NotificationStatus.FAILED
        else:
            status = NotificationStatus.FAILED
        try:
            error_msg = result["results"][0]["error"]
        except KeyError:
            error_msg = "Token not registered"
        if user is not None:
            TBNotificationRecord.objects.create(
                title=msg["title"],
                message=msg["body"],
                sender=NotificationSender.TEZBOR,
                receiver=user,
                status=status, type=NotificationType.SINGLE,
                error=error_msg)
        else:
            TBNotificationRecord.objects.create(
                title=msg["title"],
                message=msg["body"],
                sender=NotificationSender.TEZBOR,
                status=status, type=NotificationType.MULTIPLE,
                error=error_msg)

# from datetime import datetime
# time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
# key = settings.PYFCM_AGENT_SERVER_KEY
# push_service = FCMNotification(api_key=key)
# token = "cfooBcNmRxCNxP-7gSjmFe:APA91bHn9HjdMX1RZ3NYCmmPW0PL1vDpNwxlkm7L5P2N_lov2nnr3u2TVfof4r1SPPPknecmxmyYSKKCeAATiWmVC9j4IgyIp-9GzEJQUWhezZjSeOafYMJacdOcWoT8qspjWIcER4IF"
# result = push_service.notify_single_device(
#     registration_id=token, message_title="Message title", message_body=f"Hello TIME: {time}")
# print("Result....", result, type(result))

# qs = UserDevice.objects.filter(id=5)
# time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
#
# if qs.exists():
#     device = qs.first()
#     result = push_service.notify_single_device(
#         registration_id=device.registration_id, message_title="Message title", message_body=f"Hello TIME: {time}")
#     print("Result....", result, type(result))
#
# else:
#     print("ESLE....")
#********************************************
# qs = ActivationCode.objects.filter(id=54)
# check = qs.first().not_expired()
# print("S...", check, type(check))
# instance = User.objects.get(id=21)
# data = ActivationCode.objects.create(user=instance, phone=instance.phone_number)
# print("D...", data.timestamp)

