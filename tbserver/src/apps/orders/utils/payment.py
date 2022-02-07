from apps.billing.models import Transaction, UserAccount, get_tezbor_account
from apps.core.services.model_status import *


class PaymentController:

    @staticmethod
    def order_cash_type_isvalid(data):
        if 'cash_received' in data:
            cash_types = OrderCashStatus.attr_list()
            if int(data["cash_received"]) in cash_types:
                return data
            else:
                return False
        else:
            data["cash_received"] = OrderCashStatus.NOT_RECEIVED
            return data

    def control_order_status(self, order, data):
        payment_status = int(data["payment_status"])
        if payment_status == PaymentType.CASH or payment_status == PaymentType.RECEIVER_CASH:
            order.payment_status = payment_status
            return self.order_payment(order=order)
        elif payment_status == PaymentType.VIP_PAYMENT:
            if not order.customer.type == UserType.MERCHANT:
                return False
            order.payment_status = PaymentType.VIP_PAYMENT
            payer = UserAccount.objects.filter(user_id=order.customer.id, type=UserAccountType.TEZBOR).last()
            data = {
                "order": order, "payer": payer, "receiver": get_tezbor_account(),
                "paymethod": PaymentType.TEZBOR_PAYMENT, "amount": order.amount,
                "reason": TransactionType.PAID_VIP_ORDER, "status": TransactionStatus.SUCCESS
            }
            Transaction.objects.create(**data)
            return self.order_payment(order=order)
        else:
            return False

    def order_payment(self, order):
        if order.sender_address.type == AddressType.DOOR:
            order.status = OrderStatus.NEW
            order.save(update_fields=['status', 'payment_status'])
        else:
            order.status = OrderStatus.EXPECTED
            order.save(update_fields=['status', 'payment_status'])
        order.record_order_log(initiator=order.customer, car=None, comment="To'lov turi tanlandi")
        return order