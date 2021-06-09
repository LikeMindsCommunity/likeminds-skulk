import abc
import razorpay


class RazorpayManager(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'get_instance') and
                callable(subclass.get_instance) or
                NotImplemented)

    @staticmethod
    def get_instance() -> razorpay.Client:
        """
        returns razorpay client instance
        """
        raise NotImplementedError
