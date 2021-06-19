import razorpay

from django.conf import settings

from ..razorpay.razorpay_manager import RazorpayManager


class RazorpayWrapper(RazorpayManager):

    __instance__ = None

    def __init__(self) -> None:

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY, settings.RAZORPAY_SECRET))

        RazorpayWrapper.__instance__ = client

    """
        method: get_instance
        returns: razorpay instance
    """

    @staticmethod
    def get_instance() -> razorpay.client:
        if RazorpayWrapper.__instance__ is None:
            RazorpayWrapper()

        return RazorpayWrapper.__instance__
