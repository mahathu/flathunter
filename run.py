from scrapers import AdlerScraper, DegewoScraper, GewobagScraper
from send_requests import apply_to_property
from util import log, add_property_to_seen
import time
import yaml
import argparse
from termcolor import colored
import traceback

with open("config.yml", "r") as config_file:
    CONFIG = yaml.safe_load(config_file)

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

SEEN_FILE_URL = "seen_properties.txt"
SLEEP_LEN = CONFIG["sleep-len"]
N_APPLICATIONS = CONFIG["n-applications"]  # applications per ad
EMAIL_SET = [f"martin.hoffmann98+{i+1}@systemli.org" for i in range(N_APPLICATIONS)]
EMAIL_SET_ADLER = [f"martin.hoffmann98+{i+1}@systemli.org" for i in range(25)]

scrapers = [
    # GewobagScraper(CONFIG["gewobag-search-url"]),
    # DegewoScraper(CONFIG["degewo-search-url"]),
    # AdlerScraper(CONFIG["adler-search-url-xberg"]),
    AdlerScraper(CONFIG["adler-search-url-nk"]),
]


def result_filter(property):
    """returns true if result is wanted and false otherwise"""
    # TODO: perhaps make this part of the property class?
    if property.url in seen_properties:
        return False

    if any([word.lower() in property.title.lower() for word in TITLE_BLACKLIST]):
        return False

    if any([district in property.address for district in DISTRICT_BLACKLIST]):
        return False

    return True


if __name__ != "__main__":
    exit()

try:
    with open(SEEN_FILE_URL, "r") as f:
        seen_properties = [line.rstrip() for line in f.readlines()]
except IOError:
    seen_properties = []

parser = argparse.ArgumentParser()
parser.add_argument("-d", action="store_true", help="Enable debug mode")
DEBUG_ENABLED = parser.parse_args().d

if DEBUG_ENABLED:
    print(colored("Debug mode is enabled", color="red", attrs=["bold"]))
    # EMAIL_SET = ['darklightnova@hotmail.de']

while True:
    found_properties = []

    for scraper in scrapers:
        try:
            found_properties.extend(scraper.find_properties())
        except Exception as e:
            log(traceback.format_exc())

    filtered_properties = [p for p in found_properties if result_filter(p)]
    log(
        f"{len(found_properties)} properties found in total ({len(filtered_properties)} new)"
    )

    for property in filtered_properties:
        # seen_properties.append(property["url"])
        # add_property_to_seen(SEEN_FILE_URL, property["url"])

        log(f"Neues Angebot: {property}")

        # if property["company"] == "adler":
        #     apply_to_property(
        #         property["company"], property["id"], EMAIL_SET_ADLER
        #     )
        # else:
        #     apply_to_property(
        #         property["company"], property["id"], EMAIL_SET
        #     )

    time.sleep(SLEEP_LEN)
