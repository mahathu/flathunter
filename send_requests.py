import email
from bs4 import BeautifulSoup
from util import get_lines_as_list, generate_fake_email
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
    property. it will call send_application() multiple times, both with the
    provided email_set and with a number of fake personas.
    """
    print(f"Applying to {property_id} from {company}...")

    i = 0
    failed_attempts = 0
    start_time = time.time()

    while failed_attempts < 5 * len(email_set) and i < len(email_set):
        status_code, text = send_application(
            email_set[i], "Martin", "Hoffmann", company, property_id
        )

        # to obfuscate my emails with a bunch of fake emails:
        for _ in range(random.randint(1, 3)):
            fn = random.choice(FIRST_NAMES)
            ln = random.choice(LAST_NAMES)
            send_application(generate_fake_email(fn, ln), fn, ln, company, property_id)

        if status_code == 200:
            # print("✅", end="\n" if i == len(email_set)-1 else "", flush=True)
            i += 1  # use the next email
            continue

        elif (
            status_code == 409
        ):  # Property is not available anymore or already applied with given email
            # print(f"⚠️  {status_code}: {text}")
            failed_attempts += 1
            break

        else:
            print(f"⚠️  {status_code}: {text}")
            failed_attempts += 1

    delta = time.time() - start_time
    print(
        f"Sent {i}/{len(email_set)} applications in {delta:.1f}s ({failed_attempts} failed requests)."
    )


def send_application(
    mail, firstname, lastname, company, property_id, use_delay=True, use_proxy=True
):
    BASE_PAYLOAD_DATA["defaultApplicantFormDataTO"]["email"] = mail
    BASE_PAYLOAD_DATA["defaultApplicantFormDataTO"]["firstName"] = firstname
    BASE_PAYLOAD_DATA["defaultApplicantFormDataTO"]["lastName"] = lastname

    proxies = {
        "http": PROXY_URL,
        "https": PROXY_URL,
    }

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
            proxies=proxies if use_proxy else {},
        )

    except ConnectionResetError:
        print("CONNECTIONRESETERROR", end="", flush=True)  # this shouldn't ever happen
        return -1

    delay = 0
    if use_delay:
        delay = random.randint(2, 4)
    print(
        f"{firstname} {lastname} ({mail}): {response.status_code} {f'({response.text})' if not response else ''} - sleeping {delay}s"
    )
    time.sleep(delay)

    return response.status_code, response.text


def send_fake_applications(company, property_id, n=20):
    first_names_filtered = random.choices(FIRST_NAMES, k=n)
    last_names_filtered = random.choices(LAST_NAMES, k=n)

    for fn, ln in zip(first_names_filtered, last_names_filtered):
        email = generate_fake_email(fn, ln)
        send_application(email, fn, ln, company, property_id)


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


FIRST_NAMES = get_lines_as_list("firstnames.txt")
LAST_NAMES = get_lines_as_list("lastnames.txt")


if __name__ == "__main__":
    manual_apply(
        "https://www.gewobag.de/fuer-mieter-und-mietinteressenten/mietangebote/0100-01928-0110-0400/"
    )
