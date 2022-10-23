from scrapers import AdlerScraper, DegewoScraper, GewobagScraper
from properties import Identity
from send_requests import apply_to_property
from util import log, add_property_to_seen
import time
import yaml
import argparse
from termcolor import colored
import traceback


if __name__ != "__main__":
    exit()

parser = argparse.ArgumentParser()
parser.add_argument("-d", action="store_true", help="Enable debug mode")
DEBUG_ENABLED = parser.parse_args().d

if DEBUG_ENABLED:
    print(colored("Debug mode is enabled", color="red", attrs=["bold"]))
    # load alternative config here

with open("config.yml", "r") as config_file:
    CONFIG = yaml.safe_load(config_file)

SEEN_FILE_URL = "seen_properties.txt"
SLEEP_LEN = CONFIG["sleep-len"]
N_APPLICATIONS = CONFIG["n-applications"]  # applications per ad
EMAIL_SET = [f"martin.hoffmann98+{i+1}@systemli.org" for i in range(N_APPLICATIONS)]
EMAIL_SET_ADLER = [f"martin.hoffmann98+{i+1}@systemli.org" for i in range(25)]

scrapers = [
    # GewobagScraper(CONFIG["gewobag-search-url"]),
    DegewoScraper("https://immosuche.degewo.de/de/search.json?utf8=%E2%9C%93&property_type_id=1&categories%5B%5D=1&property_number=&address%5Braw%5D=&address%5Bstreet%5D=&address%5Bcity%5D=&address%5Bzipcode%5D=&address%5Bdistrict%5D=&district=&price_switch=false&price_switch=on&price_from=&price_to=&price_from=&price_to=&price_radio=null&price_from=&price_to=&qm_radio=null&qm_from=&qm_to=&rooms_radio=null&rooms_from=&rooms_to=&features%5B%5D=&wbs_required=&order=rent_total_without_vat_asc&"),
    # AdlerScraper(CONFIG["adler-search-url-xberg"]),
    # AdlerScraper(CONFIG["adler-search-url-nk"]),
]

try:
    with open(SEEN_FILE_URL, "r") as f:
        seen_properties = [line.rstrip() for line in f.readlines()]
except IOError:
    seen_properties = []


while True:
    found_properties = []

    for scraper in scrapers:
        try:
            found_properties.extend(scraper.find_properties())
        except Exception as e:
            log(traceback.format_exc())

    filtered_properties = [
        p for p in found_properties if p.is_desired and p.url not in seen_properties
    ]
    log(
        f"{len(found_properties)} properties found in total ({len(filtered_properties)} new)"
    )

    for property in filtered_properties:
        seen_properties.append(property.url)
        # add_property_to_seen(SEEN_FILE_URL, property.url)

        log(f"Neues Angebot: {property}")
        id = Identity("Johanna", "Schreiber")
        # status_code, status_text = property.apply(id)
        # log(f"{id} {property.id} {status_code} {status_text}")

    exit()
    time.sleep(SLEEP_LEN)
