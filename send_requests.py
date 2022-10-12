from bs4 import BeautifulSoup
from util import log, get_lines_as_list, generate_fake_email
from urllib.parse import quote
import requests
import json
import yaml
import time
import random

COMPANIES = {
    "degewo": "6e18d067-8058-4485-99a4-5b659bd8ad01",
    "gewobag": "78f041a8-0c9d-45ba-b290-e1e366cf2e27",
}

BASE_HEADERS = {
    "authority": "app.wohnungshelden.de",
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9,de;q=0.8",
    "content-type": "application/json",
    "dnt": "1",
    "origin": "https://app.wohnungshelden.de",
    "sec-ch-ua": '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
}

BASE_PAYLOAD_DATA = {
    "defaultApplicantFormDataTO": {
        "applicantMessage": None,
        "phoneNumber": None,
        "salutation": "MR",
        "street": None,
        "houseNumber": None,
        "zipCode": None,
        "city": None,
    },
    "saveFormDataTO": {
        "formData": {
            "numberPersonsTotal": "1",
        },
        "files": [],
    },
}


def apply_to_property(
    company, property_id, email_set, include_fakes=True, use_proxy=True
):
    """
    apply_to_property() is the main function that should be called once per
    property. it will call send_wohnungshelden_application() multiple times, both with the
    provided email_set and with a number of fake personas.
    """

    log(f"Applying to {property_id} from {company}...")

    start_time = time.time()

    application_set = []  # list of tuples: (email, fn, ln)
    for mail in email_set:
        application_set.append((mail, "Martin", "Hoffmann"))
        for _ in range(random.randint(1, 3)):
            fn = random.choice(FIRST_NAMES)
            ln = random.choice(LAST_NAMES)
            application_set.append((generate_fake_email(fn, ln), fn, ln))

    for (email, fn, ln) in application_set:
        if company == "adler":
            status_code, text = send_adler_application(email, fn, ln, property_id)

        else:
            status_code, text = send_wohnungshelden_application(
                email, fn, ln, company, property_id
            )

        log(f"{fn} {ln} ({email}): {status_code} {text}")
        time.sleep(random.randint(2, 5))

    delta = time.time() - start_time
    log(f"Sent {len(email_set)} applications in {delta:.1f}s.")


def send_adler_application(mail, fn, ln, property_id):
    # this one needs special treatment
    # TODO: make these application functions part of their respective scraper?
    mail_url_encoded = quote(mail)
    request_url = f"https://www.adler-group.com/index.php?tx_immoscoutgrabber_pi2%5B__referrer%5D%5B%40extension%5D=ImmoscoutGrabber&tx_immoscoutgrabber_pi2%5B__referrer%5D%5B%40controller%5D=ShowObjects&tx_immoscoutgrabber_pi2%5B__referrer%5D%5B%40action%5D=displaySingleExpose&tx_immoscoutgrabber_pi2%5B__referrer%5D%5Barguments%5D=YToxOntzOjI6ImlkIjtzOjk6IjEzNzA2OTk1MCI7fQ%3D%3Db0e8543fa4bbcd46de49f17f834f5a5a94c02d2a&tx_immoscoutgrabber_pi2%5B__referrer%5D%5B%40request%5D=%7B%22%40extension%22%3A%22ImmoscoutGrabber%22%2C%22%40controller%22%3A%22ShowObjects%22%2C%22%40action%22%3A%22displaySingleExpose%22%7D1ef78d7bfc1912570b7737fc000249e80b5eb13c&tx_immoscoutgrabber_pi2%5B__trustedProperties%5D=%7B%22is_mandatory%22%3A%5B1%2C1%2C1%2C1%5D%2C%22contact_firstname%22%3A1%2C%22contact_lastname%22%3A1%2C%22contact_phone%22%3A1%2C%22contact_email%22%3A1%2C%22contact_message%22%3A1%2C%22gdpr-ack%22%3A1%2C%22action%22%3A1%2C%22exposeid%22%3A1%7D5b8f74aea4017d8ee8af7d2f3f7a4f1030d56040&tx_immoscoutgrabber_pi2%5Bcontact_salutation%5D=mr&tx_immoscoutgrabber_pi2%5Bis_mandatory%5D%5B%5D=contact_salutation&tx_immoscoutgrabber_pi2%5Bcontact_firstname%5D={fn}&tx_immoscoutgrabber_pi2%5Bis_mandatory%5D%5B%5D=contact_firstname&tx_immoscoutgrabber_pi2%5Bcontact_lastname%5D={ln}&tx_immoscoutgrabber_pi2%5Bis_mandatory%5D%5B%5D=contact_lastname&tx_immoscoutgrabber_pi2%5Bcontact_phone%5D=&tx_immoscoutgrabber_pi2%5Bcontact_email%5D={mail_url_encoded}&tx_immoscoutgrabber_pi2%5Bis_mandatory%5D%5B%5D=contact_email&tx_immoscoutgrabber_pi2%5Bcontact_message%5D=&tx_immoscoutgrabber_pi2%5Bgdpr-ack%5D=&tx_immoscoutgrabber_pi2%5Bgdpr-ack%5D=true&tx_immoscoutgrabber_pi2%5Baction%5D=submitForm&tx_immoscoutgrabber_pi2%5Bexposeid%5D={property_id}&type=4276906"

    response = requests.get(request_url, proxies=PROXIES)

    return response.status_code, response.text


def send_wohnungshelden_application(
    mail, firstname, lastname, company, property_id, use_proxy=True
):
    BASE_PAYLOAD_DATA["defaultApplicantFormDataTO"]["email"] = mail
    BASE_PAYLOAD_DATA["defaultApplicantFormDataTO"]["firstName"] = firstname
    BASE_PAYLOAD_DATA["defaultApplicantFormDataTO"]["lastName"] = lastname

    company_id = COMPANIES[company]
    url = f"https://app.wohnungshelden.de/api/applicationFormEndpoint/3.0/form/create-application/{company_id}/{property_id}"
    request_headers = BASE_HEADERS | {
        "referer": f"https://app.wohnungshelden.de/public/listings/{property_id}/application?c={company_id}"
    }

    try:
        response = requests.post(
            url,
            headers=request_headers,
            data=json.dumps(BASE_PAYLOAD_DATA),
            proxies=PROXIES if use_proxy else {},
        )

    except ConnectionResetError:
        print("CONNECTIONRESETERROR", end="", flush=True)  # this shouldn't ever happen
        return -1

    return response.status_code, response.text


def send_fake_applications(company, property_id, n=20):
    first_names_filtered = random.choices(FIRST_NAMES, k=n)
    last_names_filtered = random.choices(LAST_NAMES, k=n)

    for fn, ln in zip(first_names_filtered, last_names_filtered):
        email = generate_fake_email(fn, ln)
        send_wohnungshelden_application(email, fn, ln, company, property_id)


def apply_to_stadtundland(property_id):
    base_url = "https://www.stadtundland.de/exposes/immo.{property_id}.php"
    url = base_url.format(property_id=property_id)

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    csrf_token = soup.find("input", {"name": "form-token"})["value"]


def manual_apply(url):
    property_code = url.split("/")[-2].replace("-", "%2F")
    EMAIL_SET = [f"mhoffmannpi+{i}@gmail.com" for i in range(2)]
    apply_to_property("gewobag", property_code, EMAIL_SET)


with open("secrets.yml", "r") as secrets_file:
    secrets = yaml.safe_load(secrets_file)
    API_KEY = secrets["scraper-api-key"]
    PROXY_URL = secrets["proxy-url"]
    PROXIES = {
        "http": PROXY_URL,
        "https": PROXY_URL,
    }


FIRST_NAMES = get_lines_as_list("firstnames.txt")
LAST_NAMES = get_lines_as_list("lastnames.txt")


if __name__ == "__main__":
    manual_apply(
        "https://www.gewobag.de/fuer-mieter-und-mietinteressenten/mietangebote/0100-01928-0110-0400/"
    )
