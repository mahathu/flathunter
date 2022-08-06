from scrapers import DegewoScraper, GewobagScraper
from send_requests import apply_to_property
import time

DISTRICT_BLACKLIST = ["Rudow", "Waidmannslust", "Staaken", "Marzahn"]
TITLE_BLACKLIST = ["Senior", "Selbstrenovierer", "mit WBS", "im Grünen"]
SEEN_FILE_URL = "seen_properties.txt"
SLEEP_LEN = 45
N_APPLICATIONS = 50  # applications per ad
EMAIL_SET = [f"martin.hoffmann98+{i+1}@systemli.org" for i in range(N_APPLICATIONS)]


scrapers = [
    GewobagScraper(
        "https://www.gewobag.de/fuer-mieter-und-mietinteressenten/mietangebote/?bezirke%5B%5D=friedrichshain-kreuzberg&bezirke%5B%5D=friedrichshain-kreuzberg-friedrichshain&bezirke%5B%5D=friedrichshain-kreuzberg-kreuzberg&bezirke%5B%5D=mitte&bezirke%5B%5D=mitte-gesundbrunnen&bezirke%5B%5D=mitte-moabit&bezirke%5B%5D=mitte-wedding&bezirke%5B%5D=neukoelln&bezirke%5B%5D=neukoelln-britz&bezirke%5B%5D=pankow&bezirke%5B%5D=pankow-prenzlauer-berg&bezirke%5B%5D=tempelhof-schoeneberg&nutzungsarten%5B%5D=wohnung&gesamtmiete_von=&gesamtmiete_bis=1000&gesamtflaeche_von=&gesamtflaeche_bis=&zimmer_von=&zimmer_bis=&keinwbs=1&sort-by=recent"
    ),
    DegewoScraper(
        "https://immosuche.degewo.de/de/search.json?utf8=%E2%9C%93&property_type_id=1&categories%5B%5D=1&property_number=&address%5Bstreet%5D=&address%5Bcity%5D=&address%5Bzipcode%5D=&address%5Bdistrict%5D=&district=46%2C+28%2C+29%2C+71%2C+60&price_switch=false&price_switch=on&price_from=&price_to=&price_from=&price_to=&price_radio=null&price_from=&price_to=&qm_radio=null&qm_from=&qm_to=&rooms_radio=null&rooms_from=&rooms_to=&features%5B%5D=&wbs_required=0&order=rent_total_without_vat_asc&"
    ),
]


def result_filter(result):
    """returns true if result is wanted and false otherwise"""
    if result["url"] in seen_properties:
        return False

    if any([word in result["title"] for word in TITLE_BLACKLIST]):
        return False

    if any([district in result["address"] for district in DISTRICT_BLACKLIST]):
        return False

    return True


def log(line):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {line}", flush=True)


if __name__ == "__main__":
    try:
        with open(SEEN_FILE_URL, "r") as f:
            seen_properties = [line.rstrip() for line in f.readlines()]
    except IOError:
        seen_properties = []

    while True:
        try:
            for scraper in scrapers:
                for property in filter(result_filter, scraper.get_items()):
                    seen_properties.append(property["url"])
                    log(
                        f"Neues Angebot gefunden: {property['title']}: {property['address']}"
                    )

                    apply_to_property(property["company"], property["id"], EMAIL_SET)

                    with open(
                        SEEN_FILE_URL, "a"
                    ) as f:  # will create file if not exists
                        f.write(f"{property['url']}\n")

        except Exception as e:  # this shouldn't catch KeyboardInterrupts I think
            log(f"Exception: {e}")

        log(f"Sleeping for {SLEEP_LEN} seconds.")
        time.sleep(SLEEP_LEN)
