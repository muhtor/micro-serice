from rest_framework import permissions, generics
from rest_framework.response import Response
from apps.core.services.messenger import MessageController
from .controllers import ResponseController, FilterController
from .model_status import *
from .paginations import CustomPagination
from ..authentication.tb_auth import TBTokenAuthentication
from apps.accounts.models import TBConfiguration


class ObjectPermission(MessageController, ResponseController):

    def car_permission(self):
        self.error_text = {"uz": "Avtoulov", "de": "Автоулов", "en": "Car", "ru": "Автомобиль"}
        self.code = TBResponse.CODE_4
        self.error_message = TBResponse.MSG_4
        return self.error_response()

    @staticmethod
    def get_user_role(user) -> list:
        groups = user.groups.all()
        result = []
        if groups.exists():
            for role in groups:
                result.append({"role": role.name})
        return result


class CustomOfferListView(ObjectPermission, generics.ListAPIView, CustomPagination, FilterController):
    error_text = {"uz": "Buyurtma", "de": "Буюртма", "en": "Order", "ru": "Заказ"}

    def list(self, request, *args, **kwargs):
        roles = [group["role"].lower() for group in self.get_user_role(user=request.user)]
        qs = self.get_queryset()
        print("ROLES....", qs, type(qs))
        if qs:
            if "incitydriver" in roles:
                # In city driver
                # queryset = qs.filter(customer__type=UserType.MERCHANT)
                queryset = qs.filter(
                    Q(sender_address__city__name=F('receiver_address__city__name')) |
                    Q(driver_drop_address__type=AddressType.DROP)
                )
                print("QUERYSET....", queryset, type(queryset))
                # queryset = qs.filter(driver_drop_address__type=AddressType.DROP)
            else:
                # Out city driver
                queryset = qs.filter(
                    Q(urgency=DeliveryType.EXPRESS, customer__isnull=False) |
                    Q(driver_drop_address__type=AddressType.DOOR)
                )
            if queryset:
                result = self.paginated_queryset(queryset, request)
                serializer = self.serializer_class(result, many=True)
                response = self.paginated_response(data=serializer.data)
                return Response(response)
            else:
                self.code = TBResponse.CODE_4
                self.error_message = TBResponse.MSG_4
                return self.error_response()
        else:
            self.code = TBResponse.CODE_4
            self.error_message = TBResponse.MSG_4
            return self.error_response()


class CustomListView(ObjectPermission, generics.ListAPIView, CustomPagination):
    error_text = {"uz": "Buyurtma", "de": "Буюртма", "en": "Order", "ru": "Заказ"}

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        if qs:
            result = self.paginated_queryset(qs, request)
            serializer = self.serializer_class(result, many=True)
            response = self.offer_list_response(groups=self.get_user_role(user=request.user), data=serializer.data)
            return Response(response)
        else:
            self.code = TBResponse.CODE_4
            self.error_message = TBResponse.MSG_4
            return self.error_response()


class CustomApiView(ObjectPermission, generics.GenericAPIView):
    pass


class CustomRetrieveView(ObjectPermission, generics.RetrieveAPIView):
    lookup_field = 'pk'

    def retrieve(self, request, *args, **kwargs):
        try:
            obj = self.get_object()
            serializer = self.get_serializer(obj)
            return self.success_response(result=serializer.data)
        except Exception as e:
            self.update_error_text(catch=self.kwargs["pk"])
            self.code = TBResponse.CODE_4
            self.error_message = TBResponse.MSG_4
            self.exception = e.args
            return self.error_response()


class CustomOrderDetailView(ObjectPermission, generics.RetrieveAPIView):
    lookup_field = 'pk'

    def retrieve(self, request, *args, **kwargs):
        try:
            order = self.get_object()
            if order.children.exists():
                serializer = self.get_serializer(order.children.all(), many=True)
                dimension = order.order_size
                size = {"weight": 0.0, "width": 0.0, "height": 0.0, "length": 0.0}
                if dimension:
                    size["weight"] = order.order_size.weight
                    size["width"] = order.order_size.width
                    size["height"] = order.order_size.height
                    size["length"] = order.order_size.length
                extend_timer = TBConfiguration.get_config(key="extend_order_accept_time", if_not_found=800000)  # 10 min
                package = {
                    "id": order.id,
                    "status": order.status,
                    "executor_fee": int(order.executor_fee),
                    "agent_fee": int(order.agent_fee),
                    "payment_status": order.payment_status,
                    "order_track_id": order.order_track_id,
                    "duration": order.duration,
                    "distance": order.distance,
                    "order_size": size,
                    "extend_time": str(extend_timer),
                    "bundle": order.is_in_city_order(),
                }
                return self.success_response(package=package, results=serializer.data)
            else:
                serializer = self.get_serializer(order)
                return self.success_response(result=serializer.data)
        except Exception as e:
            self.update_error_text(catch=self.kwargs["pk"])
            self.code = TBResponse.CODE_4
            self.error_message = TBResponse.MSG_4
            self.exception = e.args
            return self.error_response()


class CustomRetrieveUpdateDestroyView(ObjectPermission, generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [TBTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'


class TBResponse:

    CALCULATOR_DESCRIPTION = {
        "uz": {
            "standard": {
                "title": "Standart (3 kun)",
                "desc": "Bizning odatiy ajoyib xizmatimiz, etkazib berish muddati 3 kun ichida. Tezbor nuqtasida qoldiring yoki kuryerlik xizmatini tanlang.",
            },
            "express": {
                "title": "Tezkor (ekspress)",
                "desc": "Jo'natmangiz manzilga bir kun ichida yetib borishi uchun tushga qadar buyurtma bering va o'zingizga yaqin Tezbor nuqtasiga yoki kuryerga jo'natmangizni topshiring."
            }
        },
        "de": {
            "standard": {
                "title": "Стандарт (3 кун)",
                "desc": "Бизнинг одатий ажойиб хизматимиз, етказиб бериш муддати 3 кун ичида. Тезбор нуқтасида қолдиринг ёки курйерлик хизматини танланг."
            },
            "express": {
                "title": "Тезкор (експресс)",
                "desc": "Жўнатмангиз манзилга имкон қадар тезроқ бориши учун тушга қадар буюртма беринг ва ўзингизга яқин Тезбор нуқтасига ёки курерга жўнатмангизни топширинг."
            }
        },
        "en": {
            "standard": {
                "title": "Standard (3 day)",
                "desc": "Our usual great service, delivery in 3 days. Choose either Tezbor drop off or courier collection.",
            },
            "express": {
                "title": "Next Day",
                "desc": "Drop your parcel off at any Tezbor point or hand it over to our courier by noon to help us deliver within a day",
            }
        },
        "ru": {
            "standard": {
                "title": "Стандарт (3 день)",
                "desc": "Наш обычный отличный сервис, срок доставки - 3 дня. Выберите в посылочный магазин возврат или получение курьером.",
            },
            "express": {
                "title": "Следующий день",
                "desc": "Сделайте заказ до полудня, чтобы гарантировать доставку на следующий день.",
            }
        }
    }

    CODE_0 = 0
    MSG_0 = {
        "uz": "OK",
        "de": "ОК",
        "en": "OK",
        "ru": "ОК"
    }

    CODE_1 = 1
    MSG_1 = {
        "uz": "%s allaqachon mavjud",
        "de": "%s аллақачон мавжуд",
        "en": "%s already exist",
        "ru": "%s уже существует"
    }

    CODE_2 = 2
    MSG_2 = {
        "uz": "muvaffaqiyatli yaratildi",
        "de": "муваффақиятли яратилди",
        "en": "created successfully",
        "ru": "успешно создан"
    }

    CODE_3 = 3
    MSG_3 = {
        "uz": "kiritilgan ma'lumot(lar) noto'g'ri",
        "de": "киритилган маълумот(лар) нотўғри",
        "en": "invalid data",
        "ru": "неверные данные",
    }

    CODE_4 = 4
    MSG_4 = {
        "uz": "%s topilmadi!",
        "de": "%s топилмади!",
        "en": "%s not found!",
        "ru": "%s не найден!",
    }

    CODE_5 = 5
    MSG_5 = {
        "uz": "yaratish muvaffaqiyatsiz yakunlandi.",
        "de": "яратиш муваффақиятсиз якунланди.",
        "en": "creation failed",
        "ru": "создание не удалось",
    }

    CODE_6 = 6
    MSG_6 = {
        "uz": "%s yaroqsiz qiymat",
        "de": "%s яроқсиз қиймат",
        "en": "%s invalid value(s)",
        "ru": "%s недопустимый формат значения"
    }

    CODE_7 = 7
    MSG_7 = {
        "uz": "%s faollashtirish kutilmoqda",
        "de": "%s фаоллаштириш кутилмоқда",
        "en": "%s awaiting activation",
        "ru": "%s ожидает активации"
    }

    CODE_8 = 8
    MSG_8 = {
        "uz": "%s muvaffaqiyatli faollashtirildi",
        "de": "%s муваффақиятли фаоллаштирилди",
        "en": "%s activated successfully",
        "ru": "%s активирован успешно"
    }

    CODE_9 = 9
    MSG_9 = {
        "uz": "%s allaqachon faollashtirilgan",
        "de": "%s аллақачон фаоллаштирилган",
        "en": "%s already activated",
        "ru": "%s уже активирован"
    }

    CODE_10 = 10
    MSG_10 = {
        "uz": "%s faollashtirish kodi noto'g'ri",
        "de": "%s фаоллаштириш коди нотўғри",
        "en": "%s invalid activation code",
        "ru": "%s неверный код активации"
    }

    CODE_11 = 11
    MSG_11 = {
        "uz": "vaqt tugadi",
        "de": "вақт тугади",
        "en": "time is over",
        "ru": "время вышло"
    }

    CODE_12 = 12
    MSG_12 = {
        "uz": "muvaffaqiyatli yangilandi",
        "de": "муваффақиятли янгиланди",
        "en": "updated successfully",
        "ru": "успешно обновлено"
    }

    CODE_13 = 13
    MSG_13 = {
        "uz": "%s o'chirildi",
        "de": "%s ўчирилди",
        "en": "%s deleted",
        "ru": "%s удалено"
    }

    CODE_14 = 14
    MSG_14 = {
        "uz": "takliflar ro'yxatiga qo'shing",
        "de": "таклифлар рўйхатига қўшинг",
        "en": "add to offer list",
        "ru": "добавить в список предложений"
    }

    CODE_15 = 15
    MSG_15 = {
        "uz": "takliflar ro'yxatidan olib tashlash",
        "de": "таклифлар рўйхатидан олиб ташлаш",
        "en": "remove from offer list",
        "ru": "удалить из списка предложений"
    }

    CODE_16 = 16
    MSG_16 = {
        "uz": "",
        "de": "",
        "en": "",
        "ru": ""
    }

    CODE_17 = 17
    MSG_17 = {
        "uz": "",
        "de": "",
        "en": "",
        "ru": ""
    }

    CODE_18 = 18
    MSG_18 = {
        "uz": "%s talab qilinadi.",
        "de": "%s talab qilinadi.",
        "en": "%s talab qilinadi.",
        "ru": "%s talab qilinadi."
    }

    CODE_19 = 19
    MSG_19 = {
        "uz": "Buyurtma holati noto'g'ri",
        "de": "Буюртма ҳолати нотўғри",
        "en": "Order status is incorrect",
        "ru": "Статус заказа неверный"
    }

    CODE_20 = 20
    MSG_20 = {
        "uz": "",
        "de": "",
        "en": "",
        "ru": ""
    }

    CODE_21 = 21
    MSG_21 = {
        "uz": "",
        "de": "",
        "en": "",
        "ru": ""
    }

    CODE_22 = 22
    MSG_22 = {
        "uz": "%s bir xil",
        "de": "%s бир хил",
        "en": "%s identical",
        "ru": "%s идентичный"
    }

    CODE_23 = 23
    MSG_23 = {
        "uz": "Vaqt istisnosi",
        "de": "Вақт истисноси",
        "en": "Time exception",
        "ru": "Исключение времени"
    }

    CODE_24 = 24
    MSG_24 = {
        "uz": "Noto'g'ri buyurtma manzili",
        "de": "Нотўғри буюртма манзили",
        "en": "Incorrect order address",
        "ru": "неверный адрес заказа"
    }

    CODE_25 = 25
    MSG_25 = {
        "uz": "",
        "de": "",
        "en": "",
        "ru": ""
    }

    CODE_26 = 26
    MSG_26 = {
        "uz": "",
        "de": "",
        "en": "",
        "ru": ""
    }

    CODE_27 = 27
    MSG_27 = {
        "uz": "",
        "de": "",
        "en": "",
        "ru": ""
    }

    CODE_28 = 28
    MSG_28 = {
        "uz": "",
        "de": "",
        "en": "",
        "ru": ""
    }

    CODE_29 = 29
    MSG_29 = {
        "uz": "",
        "de": "",
        "en": "",
        "ru": ""
    }

    CODE_30 = 30
    MSG_30 = {
        "uz": "nimadir noto'g'ri bajarildi",
        "de": "нимадир нотўғри бажарилди",
        "en": "something went wrong",
        "ru": "что-то пошло не так"
    }

    CODE_31 = 31
    MSG_31 = {
        "uz": "server ishlamayapti",
        "de": "сервер ишламаяпти",
        "en": "server is not working",
        "ru": "сервер не работает"
    }

    CODE_32 = 32
    MSG_32 = {
        "uz": "Buyurtma(lar) topilmadi",
        "de": "Буюртма(лар) топилмади",
        "en": "Order(s) not found.",
        "ru": "Заказ(ы) не найдено"
    }

    CODE_33 = 33
    MSG_33 = {
        "uz": "noto'g'ri so'rov",
        "de": "нотўғри сўров",
        "en": "bad request",
        "ru": "неудачный запрос"
    }

    CODE_34 = 34
    MSG_34 = {
        "uz": "",
        "de": "",
        "en": "",
        "ru": ""
    }

    CODE_35 = 35
    MSG_35 = {
        "uz": "",
        "de": "",
        "en": "",
        "ru": ""
    }

    CODE_36 = 36
    MSG_36 = {
        "uz": "",
        "de": "",
        "en": "",
        "ru": ""
    }

    CODE_37 = 37
    MSG_37 = {
        "uz": "",
        "de": "",
        "en": "",
        "ru": ""
    }

    CODE_38 = 38
    MSG_38 = {
        "uz": "",
        "de": "",
        "en": "",
        "ru": ""
    }

    CODE_39 = 39
    MSG_39 = {
        "uz": "",
        "de": "",
        "en": "",
        "ru": ""
    }

    CODE_40 = 40
    MSG_40 = {
        "uz": "Buyurtma boshqa haydovchi tomonidan qabul qilingan",
        "de": "Буюртма бошқа ҳайдовчи томонидан қабул қилинган",
        "en": "Order was received by another driver",
        "ru": "Заказ принадлежит другому водителю"
    }

    CODE_41 = 41
    MSG_41 = {
        "uz": "Buyurtma boshqa agentga tegishli",
        "de": "Буюртма бошқа агентга тегишли",
        "en": "Order belongs to another agent",
        "ru": "Заказ принадлежит другому агенту"
    }

    # CODE_42 = 42
    # MSG_42 = {
    #     "uz": "Ekspress buyurtmalar qabul qilinmaydi",
    #     "de": "Экспресс буюртмалар қабул қилинмайди",
    #     "en": "Express orders will not be accepted",
    #     "ru": "Экспресс-заказы не принимаются"
    # }

    CODE_42 = 42
    MSG_42 = {
        "uz": "Yetkazib berish turi mos kelmadi",
        "de": "Етказиб бериш тури мос келмади",
        "en": "Delivery type not matched",
        "ru": "Тип доставки не соответствует"
    }

    CODE_43 = 43
    MSG_43 = {
        "uz": "ruxsat berilmadi",
        "de": "рухсат берилмади",
        "en": "permission denied",
        "ru": "доступ запрещен"
    }

    CODE_44 = 44
    MSG_44 = {
        "uz": "%s mos kelmaydi",
        "de": "%s мос келмайди",
        "en": "%s does not match",
        "ru": "%s не соответствует"
    }

    CODE_45 = 45
    MSG_45 = {
        "uz": "Olib ketilishi kutilayotgan buyurtma(lar)",
        "de": "Олиб кетилиши кутилаётган буюртма(лар)",
        "en": "Order(s) to be received",
        "ru": "Заказ(ы) ожидают"
    }

    CODE_46 = 46
    MSG_46 = {
        "uz": "Kutilayotgan buyurtma(lar)",
        "de": "Кутилаётган буюртма(лар)",
        "en": "Expected order(s)",
        "ru": "Ожидаемый заказ(ы)"
    }

    CODE_55 = 55
    MSG_55 = {
        "uz": "%s bir xil bulmasligi shart",
        "de": "%s бир хил булмаслиги шарт",
        "en": "%s should not be identical",
        "ru": "%s не должны быть идентичными",
    }
