import abc


class IpManager(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return ((hasattr(subclass, 'get_country_code_from_ip') and callable(subclass.get_country_code_from_ip)) or
                NotImplemented)

    @staticmethod
    def get_country_code_from_ip(ip: str) -> str:
        """
        returns country_code from ip
        """
        raise NotImplementedError
