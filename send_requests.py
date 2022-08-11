from bs4 import BeautifulSoup
import requests
import json
import yaml
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


def apply_to_property(company, property_id, email_set, use_proxy=True):
    print(f"Requesting {property_id} from {company} >", end=" ", flush=True)

    company_id = COMPANIES[company]

    url = f"https://app.wohnungshelden.de/api/applicationFormEndpoint/3.0/form/create-application/{company_id}/{property_id}"

    request_headers = BASE_HEADERS | {
        "referer": f"https://app.wohnungshelden.de/public/listings/{property_id}/application?c={company_id}"
    }

    for mail in email_set:
        BASE_PAYLOAD_DATA["defaultApplicantFormDataTO"]["email"] = mail

        try:
            url_params = {"api_key": API_KEY, "url": url, "keep_headers": "true"}
            response = requests.post(
                "http://api.scraperapi.com",
                params=url_params,
                headers=request_headers,
                data=json.dumps(BASE_PAYLOAD_DATA),
            )

        except ConnectionResetError:
            print("ConnectionResetError!")
            continue

        if response.status_code == 500:
            print("❌", end="")
            continue

        if response.status_code != 200:
            print(response.status_code, response.text)
            return 1

        print("✅", end="\n" if mail == email_set[-1] else "", flush=True)

    return 0


def apply_to_stadtundland(property_id):
    base_url = "https://www.stadtundland.de/exposes/immo.{property_id}.php"
    url = base_url.format(property_id=property_id)

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    csrf_token = soup.find("input", {"name": "form-token"})["value"]


with open("secrets.yml", "r") as secrets_file:
    secrets = yaml.safe_load(secrets_file)
    API_KEY = secrets["scraper-api-key"]

if __name__ == "__main__":
    # testing playground
    EMAIL_SET = [f"test2{randint(100,10000)}@systemli.org"]
    apply_to_property("gewobag", "0100%2F01929%2F0301%2F0063", EMAIL_SET)
