from django.db.models import Q, F
from rest_framework.response import Response
from apps.accounts.api.v1.serializers import UserCreateSerializer
from apps.accounts.models import User, UserFilter
from apps.core.services.model_status import UserStatus, UserType
from apps.core.services.response import StatusCode


class RequestController:

    def __init__(self, request):
        self.request = request

    def get_language(self):
        """
        Public method
        @return: request headers language
        """
        return self.__check_language()

    def __check_language(self):
        """Private method"""
        header = self.request.headers
        if 'Accept-Language' in header:
            lang = header['Accept-Language'][:2]
        else:
            lang = 'uz'
        return lang


class ResponseController(RequestController):

    code = 0
    success_message: dict = {"uz": "OK", "de": "ОК", "en": "OK", "ru": "ОК"}
    error_message: dict = {"uz": "", "de": "", "en": "", "ru": ""}
    error_text: dict = {"uz": "", "de": "", "en": "", "ru": ""}
    exception: tuple = ""

    def success_response(self, *args, **kwargs):
        lang = self.get_language()
        msg_by_language = self.success_message.get(lang)
        response = {'success': True, 'code': self.code, 'message': msg_by_language}
        if kwargs:
            response.update({key: kwargs[key] for key in kwargs})
        return Response(response)

    def update_error_text(self, catch):
        self.error_text.update(dict.fromkeys(['uz', 'de', 'en', 'ru'], catch))

    def error_response(self):
        lang = self.get_language()
        error_by_language = self.error_text.get(lang)
        try:
            message_by_language = self.error_message.get(lang) % error_by_language
        except TypeError:
            message_by_language = self.error_message.get(lang)
        response = {'success': False, 'code': self.code, 'message': message_by_language}
        if self.exception:
            response['debug'] = self.exception
        return Response(response)


class UserController:

    @staticmethod
    def response(success, code, msg):
        return {"success": success, "code": code, "message": msg}

    def device_is_changed(self, qs, app):
        annotate = qs.annotate(user_types=F('type').bitand(app)).filter(user_types__gt=0)
        if annotate.exists():
            return False
        else:
            return True

    def create_or_update_user(self, user: User = None, data=dict):
        if user:
            if user.type != UserType.CUSTOMER:
                user.status = UserStatus.TOBEACTIVATED
                user.save(update_fields=['status'])
            return self.update_exist_user(user=user, data=data)
        else:
            return self.create_new_user(data=data)

    def create_new_user(self, data):
        serializer = UserCreateSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            if serializer.instance.user_sms.filter(activated=False):
                return self.response(success=True, code=StatusCode.STATUS_0_CODE, msg=StatusCode.STATUS_0_MSG)
            else:
                return self.response(success=False, code=StatusCode.STATUS_5_CODE, msg=StatusCode.STATUS_5_MSG)
        else:
            return self.response(success=False, code=StatusCode.STATUS_5_CODE, msg=StatusCode.STATUS_5_MSG)

    def update_exist_user(self, user: User, data):
        pass

    def user_exists(self, phone, app_type):
        qs = User.objects.filter(phone_number=phone, status=UserStatus.ACTIVATED)
        if qs.exists():
            user = qs.first()
            if self.device_is_changed(qs=qs, app=app_type):
                new_type_user = user.type + app_type
                user.type = new_type_user
                user.save(update_fields=['type'])
                return user
            else:
                pass
        else:
            print("404 ...")


class FilterController:

    @staticmethod
    def delete_user_filter(user_id):
        qs = UserFilter.objects.filter(user_id=user_id)
        if qs.exists():
            qs.delete()

    def create_user_filter(self, **data):
        try:
            obj = UserFilter.objects.create(**data)
            return obj
        except Exception as e:
            return e.args





