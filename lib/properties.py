from datetime import datetime
import json
import logging
from typing import Tuple

import requests
from requests.exceptions import ProxyError
from bs4 import BeautifulSoup
from urllib.parse import quote

from .identity import Identity


class Property(object):
    def __init__(self, company, address, zip_code, sqm, rent, title, url, id) -> None:
        self.company = company
        self.address = address
        self.zip_code = zip_code
        self.sqm = sqm
        self.rent = rent
        self.title = title
        self.url = url
        self.id = id

        self.found_at = datetime.now()
        self.filter_status = "unfiltered"

    def as_dict(self) -> dict:
        """Return a dict representation of the property, excluding methods and private attributes.
        This function is called when serializing the property to the archive file.
        """
        return dict(
            (key, value)
            for key, value in self.__dict__.items()
            if not callable(value) and not key.startswith("__")
        )

    def __str__(self) -> str:
        status_emoji = "✅" if self.filter_status == "OK" else "🥲"
        return f"<{status_emoji} {self.company}/{self.address}>"

    def apply(
        self, identity: Identity, proxies: dict[str, str] = None
    ) -> Tuple[int, str]:
        """Send a single application to a given property and return the status code
        and status text of the final request."""
        logging.error("ERROR: apply should only be called on subclasses of Property.")
        raise NotImplementedError


class AdlerProperty(Property):
    def apply(
        self, identity: Identity, proxies: dict[str, str] = None
    ) -> Tuple[int, str]:  # overrides Property.apply()
        mail_url_encoded = quote(identity.email)
        request_url = f"https://www.adler-group.com/index.php?tx_immoscoutgrabber_pi2%5B__referrer%5D%5B%40extension%5D=ImmoscoutGrabber&tx_immoscoutgrabber_pi2%5B__referrer%5D%5B%40controller%5D=ShowObjects&tx_immoscoutgrabber_pi2%5B__referrer%5D%5B%40action%5D=displaySingleExpose&tx_immoscoutgrabber_pi2%5B__referrer%5D%5Barguments%5D=YToxOntzOjI6ImlkIjtzOjk6IjEzNzA2OTk1MCI7fQ%3D%3Db0e8543fa4bbcd46de49f17f834f5a5a94c02d2a&tx_immoscoutgrabber_pi2%5B__referrer%5D%5B%40request%5D=%7B%22%40extension%22%3A%22ImmoscoutGrabber%22%2C%22%40controller%22%3A%22ShowObjects%22%2C%22%40action%22%3A%22displaySingleExpose%22%7D1ef78d7bfc1912570b7737fc000249e80b5eb13c&tx_immoscoutgrabber_pi2%5B__trustedProperties%5D=%7B%22is_mandatory%22%3A%5B1%2C1%2C1%2C1%5D%2C%22contact_firstname%22%3A1%2C%22contact_lastname%22%3A1%2C%22contact_phone%22%3A1%2C%22contact_email%22%3A1%2C%22contact_message%22%3A1%2C%22gdpr-ack%22%3A1%2C%22action%22%3A1%2C%22exposeid%22%3A1%7D5b8f74aea4017d8ee8af7d2f3f7a4f1030d56040&tx_immoscoutgrabber_pi2%5Bcontact_salutation%5D=mr&tx_immoscoutgrabber_pi2%5Bis_mandatory%5D%5B%5D=contact_salutation&tx_immoscoutgrabber_pi2%5Bcontact_firstname%5D={identity.firstname}&tx_immoscoutgrabber_pi2%5Bis_mandatory%5D%5B%5D=contact_firstname&tx_immoscoutgrabber_pi2%5Bcontact_lastname%5D={identity.lastname}&tx_immoscoutgrabber_pi2%5Bis_mandatory%5D%5B%5D=contact_lastname&tx_immoscoutgrabber_pi2%5Bcontact_phone%5D=&tx_immoscoutgrabber_pi2%5Bcontact_email%5D={mail_url_encoded}&tx_immoscoutgrabber_pi2%5Bis_mandatory%5D%5B%5D=contact_email&tx_immoscoutgrabber_pi2%5Bcontact_message%5D=&tx_immoscoutgrabber_pi2%5Bgdpr-ack%5D=&tx_immoscoutgrabber_pi2%5Bgdpr-ack%5D=true&tx_immoscoutgrabber_pi2%5Baction%5D=submitForm&tx_immoscoutgrabber_pi2%5Bexposeid%5D={self.id}&type=4276906"

        # TODO: add fake request headers to application
        try:
            response = requests.get(request_url, proxies=proxies)
        except ProxyError:
            logging.error("Proxy error")
            return 0, "Proxy error"

        return response.status_code, response.text


class WohnungsheldenProperty(Property):
    # gewobag and degewo use the same Wohnungshelden backend, so they
    # get the same class here
    def apply(
        self, identity: Identity, proxies: dict[str, str] = None
    ) -> Tuple[int, str]:
        """This function uses default data from request_data.json,
        modifies it and makes a request to the Wohnungshelden API."""
        with open("data/request_data.json", "r") as f:
            request_data = json.load(f)

        BASE_PAYLOAD_DATA = request_data["base_payload_data"]
        BASE_HEADERS = request_data["base_headers"]

        COMPANY_IDS = {
            "degewo": "6e18d067-8058-4485-99a4-5b659bd8ad01",
            "gewobag": "78f041a8-0c9d-45ba-b290-e1e366cf2e27",
        }

        BASE_PAYLOAD_DATA["defaultApplicantFormDataTO"]["email"] = identity.email
        BASE_PAYLOAD_DATA["defaultApplicantFormDataTO"][
            "firstName"
        ] = identity.firstname
        BASE_PAYLOAD_DATA["defaultApplicantFormDataTO"]["lastName"] = identity.lastname

        company_id = COMPANY_IDS[self.company]

        url = f"https://app.wohnungshelden.de/api/applicationFormEndpoint/3.0/form/create-application/{company_id}/{self.id}"
        request_headers = BASE_HEADERS | {
            "referer": f"https://app.wohnungshelden.de/public/listings/{self.id}/application?c={company_id}"
        }

        if self.company == "gewobag":
            # gewobag added some new fields to their application form
            # in order to not send them to degewo properties by accident
            # we add them in here manually
            # TODO: make this more elegant
            BASE_PAYLOAD_DATA["saveFormDataTO"]["formData"] = request_data[
                "gewobag_formdata"
            ]

        try:
            response = requests.post(
                url,
                headers=request_headers,
                data=json.dumps(BASE_PAYLOAD_DATA),
                proxies=proxies,
            )
        except ProxyError:
            logging.error("Proxy error")
            return 0, "Proxy error"

        return response.status_code, response.text


class SULProperty(Property):
    """apply to stadtundland property"""

    def apply(
        self, identity: Identity, proxies: dict[str, str] = None
    ) -> Tuple[int, str]:
        base_url = "https://www.stadtundland.de/exposes/immo.{property_id}.php"
        url = base_url.format(property_id=self.id)

        response = requests.get(url)
        soup = BeautifulSoup(response.text, "lxml")
        csrf_token = soup.find("input", {"name": "form-token"})["value"]
