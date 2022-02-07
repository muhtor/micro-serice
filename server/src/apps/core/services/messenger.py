from .tb_pusher import TBPusher
from apps.accounts.models import ActivationCode, ActivationType


class MessageController(TBPusher):

    def send_sms_order_sender(self, order):
        """Send SMS for order sender:"""
        phone = order.sender_phone
        message = ActivationCode.get_order_sender_sms_text()
        text = str(message) % order.order_track_id
        try:
            confirmation = ActivationCode.objects.create(
                user=order.customer, phone=phone,
                code=order.secure_code, sms_type=ActivationType.ORDER,
                text=text)
            confirmation.send_sms()
        except Exception as e:
            return str(e.args[0])

    def send_sms_order_receiver(self, order):
        """Send SMS for order receiver:"""
        phone = order.receiver_phone
        message = ActivationCode.get_order_receiver_sms_text()
        text = str(message) % (order.order_track_id, order.secure_code)
        print("receiver sms ... ", text)
        try:
            confirmation = ActivationCode.objects.create(
                user=order.customer,
                phone=phone,
                code=order.secure_code,
                sms_type=ActivationType.ORDER,
                text=text)
            confirmation.send_sms()
        except Exception as e:
            return str(e.args[0])


