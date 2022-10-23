from bs4 import BeautifulSoup
from util import log, get_lines_as_list, generate_fake_email
import requests
import yaml
import time
import random


def apply_to_property(company, property_id, email_set):
    """
    apply_to_property() is the main function that should be called once per
    property. it will call send_wohnungshelden_application() multiple times, both with the
    provided email_set and with a number of fake personas.
    """

    log(f"Applying to {property_id} from {company}...")

    start_time = time.time()

    application_set = []  # list of tuples: (email, fn, ln)
    for mail in email_set:
        application_set.append((mail, "Martin", "Hoffmann"))  # TODO don't hardcode this
        for _ in range(random.randint(1, 3)):
            fn = random.choice(FIRST_NAMES)
            ln = random.choice(LAST_NAMES)
            application_set.append((generate_fake_email(fn, ln), fn, ln))

    for (email, fn, ln) in application_set:
        if company == "adler":
            status_code, text = send_adler_application(email, fn, ln, property_id)

        elif company == "stadtundland":
            pass

        else:
            status_code, text = send_wohnungshelden_application(
                email, fn, ln, company, property_id
            )

        log(f"{fn} {ln} ({email}): {status_code} {text}")
        time.sleep(random.randint(2, 5))

    delta = time.time() - start_time
    log(f"Sent {len(email_set)} applications in {delta:.1f}s.")


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
    PROXY_URL = secrets["proxy-url"]
    PROXIES = {
        "http": PROXY_URL,
        "https": PROXY_URL,
    }


FIRST_NAMES = get_lines_as_list("firstnames.txt")
LAST_NAMES = get_lines_as_list("lastnames.txt")
