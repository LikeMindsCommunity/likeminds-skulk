import geoip2.database
import geoip2.errors

from ..ip.ip_manager import IpManager


class IpWrapper(IpManager):

    __instance__ = None

    def __init__(self) -> None:

        reader = geoip2.database.Reader('./GeoIP2-Country.mmdb')

        IpWrapper.__instance__ = reader

    @staticmethod
    def get_country_code_from_ip(ip: str) -> str:

        if IpWrapper.__instance__ is None:
            IpWrapper()

        reader = IpWrapper.__instance__

        try:
            response = reader.country(ip)
            country_code = response.country.iso_code
        except geoip2.errors.AddressNotFoundError:
            country_code = 'IN'

        return country_code
