from bs4 import BeautifulSoup
import requests
import json
import yaml

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


def apply_to_property(company, property_id, email_set):
    print(company, property_id, end=" ", flush=True)

    company_id = COMPANIES[company]

    api_url = f"https://app.wohnungshelden.de/api/applicationFormEndpoint/3.0/form/create-application/{company_id}/{property_id}"
    url = PROXY_URL.format(api_key=API_KEY, url=api_url)

    request_headers = BASE_HEADERS | {
        "referer": f"https://app.wohnungshelden.de/public/listings/{property_id}/application?c={company_id}"
    }

    for mail in email_set:
        BASE_PAYLOAD_DATA["defaultApplicantFormDataTO"]["email"] = mail

        try:
            response = requests.request(
                "POST", url, headers=request_headers, data=json.dumps(BASE_PAYLOAD_DATA)
            )
        except ConnectionResetError:
            print("ConnectionResetError!")
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

    formdata = {
        "form": "stadtundland-prospectForm",
        "title[]": "mr",
        "title[]": "__last__",
        "name[]": "asd",
        "firstname[]": "asd",
        "phone[]": "34",
        "email[]": "sadas@asda.de",
        "subsidized_housing[]": "false",
        "subsidized_housing[]": "__last__",
        "privacyProtectionAccepted[]": "true",
        "privacyProtectionAccepted[]": "__last__",
        "form-token": csrf_token,
        "action": "submit",
    }
    payload = f"form=stadtundland-prospectForm&title%5B%5D=mr&title%5B%5D=__last__&name%5B%5D=nachn&firstname%5B%5D=vorn&street%5B%5D=&zip%5B%5D=&city%5B%5D=&phone%5B%5D=015222234568&email%5B%5D=mzdhyhrenuifmizjzqew%40nthrw.com&subsidized_housing%5B%5D=false&subsidized_housing%5B%5D=__last__&privacyProtectionAccepted%5B%5D=true&privacyProtectionAccepted%5B%5D=__last__&inpQuestion=&form-token={csrf_token}&action=submit"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Language": "en-US,en;q=0.9,de;q=0.8",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": "bookmarks=%5B%5D; cookies-accepted=true; bookmarks=%5B%5D",
        "DNT": "1",
        "Origin": "https://www.stadtundland.de",
        "Referer": "https://www.stadtundland.de/exposes/immo.MO_1050_8106_130.php",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
        "sec-ch-ua": '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    soup = BeautifulSoup(response.text, "lxml")

    print(csrf_token)

    error = soup.find("div", class_="SP-Errors__anchor")
    if error:
        print(error.text)
        return 1


with open("secrets.yml", "r") as secrets_file:
    secrets = yaml.safe_load(secrets_file)
    API_KEY = secrets["scraper-api-key"]
    PROXY_URL = "http://api.scraperapi.com?api_key={api_key}&url={url}"

if __name__ == "__main__":
    # testing playground
    # EMAIL_SET = [f"BLABsLA+{i+1}@af.org" for i in range(3)]
    # apply_to_property('degewo', 'W1400.40386.0270-0501', EMAIL_SET)
    pass
