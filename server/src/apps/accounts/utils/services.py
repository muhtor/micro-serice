from datetime import timedelta
from django.utils import timezone
from apps.core.services.controllers import ResponseController
from ..models import ActivationCode, TBConfiguration, User, TBUserToken
from apps.core.services.validators import ImageController
from ...billing.models import Transaction, get_tezbor_account, UserAccount
from ...core.services.generics import TBResponse
from ...core.services.model_status import *


class TBException(ResponseController):

    def phone_number_isvalid(self):
        phone = self.request.data['phone_number']
        if len(phone) != 13 or not phone[1:].isnumeric() or phone[:4] != '+998' or phone[4:6] == "69":
            return False
        else:
            return True

    def user_exists(self, phone):
        if not self.phone_number_isvalid():
            self.update_error_text(catch=phone)
            self.code = TBResponse.CODE_6
            self.error_message = TBResponse.MSG_6
            return self.error_response()
        qs_user = User.objects.filter(phone_number=phone)
        if qs_user.exists():
            user = qs_user.first()
            self.update_error_text(catch=phone)
            if user.status == UserStatus.NOTACTIVATED:
                self.code = TBResponse.CODE_7
                self.error_message = TBResponse.MSG_7
            else:
                self.code = TBResponse.CODE_1
                self.error_message = TBResponse.MSG_1
            return self.error_response()
        else:
            return False


class AccountController(TBException, ImageController):

    def __init__(self, request=None):
        super().__init__(request)
        self.request = request

    @staticmethod
    def authentication(user, device, meta, dt):
        token = TBUserToken.objects.create(user=user, device_token=device, user_agent=str(meta), device_type=dt)
        return token.key

    @staticmethod
    def delete_access_token(token):
        qs = TBUserToken.objects.filter(key=token)
        if qs.exists():
            qs.delete()
            return True
        else:
            return False

    @staticmethod
    def delete_expired_code(phone, sms_type):
        qs_act = ActivationCode.objects.filter(phone=phone, sms_type=sms_type)
        if qs_act.exists():
            qs_act.delete()

    @staticmethod
    def not_expired(obj):
        now = timezone.now()
        timeout = TBConfiguration.get_config(key="expiration_sms_confirmation", if_not_found=180000)
        end_time = obj.timestamp + timedelta(milliseconds=int(timeout))
        if now > end_time:
            return True
        else:
            return False

    def _get_or_create_confirmation_code(self, user, phone, sms_type):
        qs = ActivationCode.objects.filter(phone=phone, activated=False, sms_type=sms_type)
        if qs.exists():
            code = qs.first()
            is_not_expired = self.not_expired(obj=code)
            if not is_not_expired:
                obj = code
            else:
                self.delete_expired_code(phone=phone, sms_type=sms_type)
                obj = ActivationCode.objects.create(user=user, phone=phone, sms_type=sms_type)
        else:
            self.delete_expired_code(phone=phone, sms_type=sms_type)
            obj = ActivationCode.objects.create(user=user, phone=phone, sms_type=sms_type)
        return obj

    def resend_sms(self, user, phone, sms_type):
        code_created = self._get_or_create_confirmation_code(user=user, phone=phone, sms_type=sms_type)
        if code_created:
            return True
        else:
            return False

    def set_referrer(self, user):
        data = self.request.data
        if "referrer" in data:
            qs = User.objects.filter(phone_number=data["referrer"])
            if qs.exists() and user.referrer is None:
                referrer = qs.first()
                user.referrer = referrer
                user.save(update_fields=["referrer"])

    def update_referrer_balance(self, user):
        referral_fee = TBConfiguration.get_config(key="referral_fee", if_not_found=5000)
        bonus = int(referral_fee)
        tb_account = get_tezbor_account()
        receivers = UserAccount.objects.filter(user=user.referrer, type=UserAccountType.TEZBOR)
        if tb_account and receivers.exists():
            receiver = receivers.first()
            try:
                Transaction.objects.create(
                    payer=tb_account,
                    receiver=receiver,
                    paymethod=PaymentType.TEZBOR_PAYMENT,
                    reason=TransactionType.RECEIVED_BY_REFERRING,
                    amount=bonus)
            except Exception as e:
                print("update_referrer_balance......", e.args)


    def get_tb_app_type(self):
        data = self.request.data
        # print("get_tb_app_type...", data)
        if "app_type" in data:
            return data["app_type"]
        else:
            return ApplicationType.CUSTOMER_APP

    def send_activation_code(self, user, phone):
        if user.status == UserStatus.TOBEACTIVATED or user.status == UserStatus.ACTIVATED or user.status == UserStatus.NOTACTIVATED:
            if self.resend_sms(user=user, phone=phone, sms_type=ActivationType.LOGIN):
                return self.success_response()
            else:
                self.code = TBResponse.CODE_30
                self.error_message = TBResponse.MSG_30
                return self.error_response()
        else:
            self.code = TBResponse.CODE_3
            self.error_message = TBResponse.MSG_3
            return self.error_response()



