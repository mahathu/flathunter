import requests
import json
from random import randint

COMPANIES = {
    'degewo': {
        'company_id': '6e18d067-8058-4485-99a4-5b659bd8ad01',
        'property_id_transformer': lambda id: id.replace('-', '.', 2),
    },
    'gewobag': {
        'company_id': '78f041a8-0c9d-45ba-b290-e1e366cf2e27',
        'property_id_transformer': lambda id: id.replace('-', '%2F'),
    },
}

BASE_HEADERS = {
    'authority': 'app.wohnungshelden.de',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9,de;q=0.8',
    'content-type': 'application/json',
    'dnt': '1',
    'origin': 'https://app.wohnungshelden.de',
    'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
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
        "city": None
    },
    "saveFormDataTO": {
        "formData": {"numberPersonsTotal": "1",},
        "files": []
    }
}

def apply_to_property(company, property_id, email_set):
    print(company, property_id, end=' ', flush=True)

    company_id = COMPANIES[company]['company_id']
    # this is handled in scraper already
    # property_id = COMPANIES[company]['property_id_transformer'](property_id)

    url = f"https://app.wohnungshelden.de/api/applicationFormEndpoint/3.0/form/create-application/{company_id}/{property_id}"
    request_headers = BASE_HEADERS | {'referer': f'https://app.wohnungshelden.de/public/listings/{property_id}/application?c={company_id}'}

    for mail in email_set:
        BASE_PAYLOAD_DATA['defaultApplicantFormDataTO']['email'] = mail

        try:
            response = requests.request("POST", url, headers=request_headers, data=json.dumps(BASE_PAYLOAD_DATA))
        except ConnectionResetError:
            print("ConnectionResetError!")
            continue

        if response.status_code != 200:
            print(response.status_code, response.text)
            return 1

        print('✅', 
            end = '\n' if mail==email_set[-1] else '', 
            flush = True)
    
    return 0

if __name__ == '__main__':
    # testing playground
    EMAIL_SET = [f"BLABsLA+{i+1}@af.org" for i in range(4)]
    apply_to_property('gewobag', '0100%2F01032%2F1101%2F0270', EMAIL_SET)