from ..payment_page.payment_page_manager import PaymentPageManeger
from .models import PaymentPageMeta


class PaymentPageImpl(PaymentPageManeger):

    def __init__(self, community_id: str = None, payment_page_instance: PaymentPageMeta = None):
        self.community_id = community_id
        self.payment_page_instance = payment_page_instance

    def get_community_id(self) -> str:
        return self.community_id

    def get_payment_page_instance(self) -> PaymentPageMeta:
        return self.payment_page_instance

    def set_community_id(self, community_id) -> None:
        self.community_id = community_id

    def set_payment_page_instance(self, payment_page_instance) -> None:
        self.payment_page_instance = payment_page_instance
