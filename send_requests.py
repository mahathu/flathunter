from bs4 import BeautifulSoup
import requests
import json
import yaml
import time
from random import randint

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
        "firstName": "Martin",
        "lastName": "Hoffmann",
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


def send_application(mail, url, request_headers, use_proxy=True):
    BASE_PAYLOAD_DATA["defaultApplicantFormDataTO"]["email"] = mail
    # proxy_headers = {f"Spb-{key}": value for key, value in request_headers.items()}
    proxies = {
        "http": PROXY_URL,
        "https": PROXY_URL,
    }
    try:
        # url_params = {"api_key": API_KEY, "url": url, "forward_headers": "true"}
        response = requests.post(
            url,
            headers=request_headers,
            data=json.dumps(BASE_PAYLOAD_DATA),
        )

    except ConnectionResetError:
        print("CONNECTIONRESETERROR", end="", flush=True)  # this shouldn't ever happen
        return -1

    return response.status_code, response.text


def apply_to_property(company, property_id, email_set, use_proxy=True):
    print(f"Requesting {property_id} from {company}...")

    company_id = COMPANIES[company]

    url = f"https://app.wohnungshelden.de/api/applicationFormEndpoint/3.0/form/create-application/{company_id}/{property_id}"

    request_headers = BASE_HEADERS | {
        "referer": f"https://app.wohnungshelden.de/public/listings/{property_id}/application?c={company_id}"
    }

    i = 0
    failed_attempts = 0
    start_time = time.time()

    while failed_attempts < 5 * len(email_set) and i < len(email_set):
        status_code, text = send_application(email_set[i], url, request_headers)

        if status_code == 200:
            print("✅", end="\n" if i == len(email_set)-1 else "", flush=True)
            i += 1  # use the next email
            continue

        elif status_code == 409: # Property is not available anymore
            print(f"⚠️  {status_code}: {text}")
            break

        else:
            print(f"⚠️  {status_code}: {text}")
            failed_attempts += 1

    delta = time.time() - start_time
    print(
        f"\nSent {i}/{len(email_set)} applications in {delta:.1f}s ({failed_attempts} failed requests)."
    )


def apply_to_stadtundland(property_id):
    base_url = "https://www.stadtundland.de/exposes/immo.{property_id}.php"
    url = base_url.format(property_id=property_id)

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    csrf_token = soup.find("input", {"name": "form-token"})["value"]


with open("secrets.yml", "r") as secrets_file:
    secrets = yaml.safe_load(secrets_file)
    API_KEY = secrets["scraper-api-key"]
    PROXY_URL = secrets["proxy-url"]

if __name__ == "__main__":
    # testing playground
    EMAIL_SET = [f"test2{randint(100,10000)}@mail.org" for i in range(3)]
    apply_to_property("gewobag", "0100%2F01033%2F0301%2F0064", EMAIL_SET)
