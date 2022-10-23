import requests
import yaml
from util import generate_fake_email, log
from urllib.parse import quote
from typing import Tuple
import json

with open("secrets.yml", "r") as secrets_file:
    secrets = yaml.safe_load(secrets_file)
    PROXY_URL = secrets["proxy-url"]
    PROXIES = {
        "http": PROXY_URL,
        "https": PROXY_URL,
    }


DISTRICT_BLACKLIST = ["Rudow", "Waidmannslust", "Staaken", "Marzahn", "Lichtenrade"]
TITLE_BLACKLIST = [
    "Single",
    "Senior",
    "Selbstrenovierer",
    "mit WBS",
    "im Grünen",
    "WBS mit besonderem Wohnbedarf",
    "WBS erforderlich",
    "WBS-fähigem",
    "Rollstuhlfahrer",
    "WBS nötig",
]


class Identity:
    def __init__(self, firstname, lastname, email=None) -> None:
        """Create a new identity. If no email is given, one is generated."""
        self.firstname = firstname
        self.lastname = lastname
        if email:
            self.email = email
        else:
            self.email = generate_fake_email(firstname, lastname)

    def __str__(self) -> str:
        return f"{self.firstname} {self.lastname} <{self.email}>"


class Property(object):
    def __init__(self, company, address, title, url, id) -> None:
        self.company = company
        self.address = address
        self.title = title
        self.url = url
        self.id = id

        self.is_desired = True
        if any([word.lower() in self.title.lower() for word in TITLE_BLACKLIST]) or any(
            [d.lower() in self.address.lower() for d in DISTRICT_BLACKLIST]
        ):
            self.is_desired = False

    def __str__(self) -> str:
        return f"[{self.company.upper()}] {self.title} ({self.address})"

    def apply(self, identity: Identity) -> Tuple[int, str]:
        """Sends a single application to a given property and returns the status code
        and status text of the final request."""
        log(f"{identity} is applying to {self.id}.")
        # base case should be for default wohnungshelden type application


class AdlerProperty(Property):
    def apply(
        self, identity: Identity
    ) -> Tuple[int, str]:  # overrides Property.apply()
        log(f"{identity} is applying to adler prop {self.id}.")
        mail_url_encoded = quote(identity.email)
        request_url = f"https://www.adler-group.com/index.php?tx_immoscoutgrabber_pi2%5B__referrer%5D%5B%40extension%5D=ImmoscoutGrabber&tx_immoscoutgrabber_pi2%5B__referrer%5D%5B%40controller%5D=ShowObjects&tx_immoscoutgrabber_pi2%5B__referrer%5D%5B%40action%5D=displaySingleExpose&tx_immoscoutgrabber_pi2%5B__referrer%5D%5Barguments%5D=YToxOntzOjI6ImlkIjtzOjk6IjEzNzA2OTk1MCI7fQ%3D%3Db0e8543fa4bbcd46de49f17f834f5a5a94c02d2a&tx_immoscoutgrabber_pi2%5B__referrer%5D%5B%40request%5D=%7B%22%40extension%22%3A%22ImmoscoutGrabber%22%2C%22%40controller%22%3A%22ShowObjects%22%2C%22%40action%22%3A%22displaySingleExpose%22%7D1ef78d7bfc1912570b7737fc000249e80b5eb13c&tx_immoscoutgrabber_pi2%5B__trustedProperties%5D=%7B%22is_mandatory%22%3A%5B1%2C1%2C1%2C1%5D%2C%22contact_firstname%22%3A1%2C%22contact_lastname%22%3A1%2C%22contact_phone%22%3A1%2C%22contact_email%22%3A1%2C%22contact_message%22%3A1%2C%22gdpr-ack%22%3A1%2C%22action%22%3A1%2C%22exposeid%22%3A1%7D5b8f74aea4017d8ee8af7d2f3f7a4f1030d56040&tx_immoscoutgrabber_pi2%5Bcontact_salutation%5D=mr&tx_immoscoutgrabber_pi2%5Bis_mandatory%5D%5B%5D=contact_salutation&tx_immoscoutgrabber_pi2%5Bcontact_firstname%5D={identity.firstname}&tx_immoscoutgrabber_pi2%5Bis_mandatory%5D%5B%5D=contact_firstname&tx_immoscoutgrabber_pi2%5Bcontact_lastname%5D={identity.lastname}&tx_immoscoutgrabber_pi2%5Bis_mandatory%5D%5B%5D=contact_lastname&tx_immoscoutgrabber_pi2%5Bcontact_phone%5D=&tx_immoscoutgrabber_pi2%5Bcontact_email%5D={mail_url_encoded}&tx_immoscoutgrabber_pi2%5Bis_mandatory%5D%5B%5D=contact_email&tx_immoscoutgrabber_pi2%5Bcontact_message%5D=&tx_immoscoutgrabber_pi2%5Bgdpr-ack%5D=&tx_immoscoutgrabber_pi2%5Bgdpr-ack%5D=true&tx_immoscoutgrabber_pi2%5Baction%5D=submitForm&tx_immoscoutgrabber_pi2%5Bexposeid%5D={self.id}&type=4276906"

        response = requests.get(request_url, proxies=PROXIES)

        return response.status_code, response.text


class WHProperty(Property):
    # gewobag and degewo use the same Wohnungshelden backend, so they
    # get the same class here
    def apply(self, identity: Identity) -> Tuple[int, str]:
        """This function uses default data from request_data.json,
        modifies it and makes a request to the Wohnungshelden API."""
        with open('request_data.json', 'r') as f:
            request_data = json.load(f)

        BASE_PAYLOAD_DATA = request_data['base_payload_data']
        BASE_HEADERS = request_data['base_headers']

        COMPANY_IDS = {
            "degewo": "6e18d067-8058-4485-99a4-5b659bd8ad01",
            "gewobag": "78f041a8-0c9d-45ba-b290-e1e366cf2e27",
        }

        BASE_PAYLOAD_DATA["defaultApplicantFormDataTO"]["email"] = identity.email
        BASE_PAYLOAD_DATA["defaultApplicantFormDataTO"]["firstName"] = identity.firstname
        BASE_PAYLOAD_DATA["defaultApplicantFormDataTO"]["lastName"] = identity.lastname

        company_id = COMPANY_IDS[self.company]

        url = f"https://app.wohnungshelden.de/api/applicationFormEndpoint/3.0/form/create-application/{company_id}/{self.id}"
        request_headers = BASE_HEADERS | {
            "referer": f"https://app.wohnungshelden.de/public/listings/{self.id}/application?c={company_id}"
        }

        response = requests.post(
            url,
            headers=request_headers,
            data=json.dumps(BASE_PAYLOAD_DATA),
            proxies=PROXIES,
        )

        return response.status_code, response.text