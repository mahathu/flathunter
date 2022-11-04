from distutils.debug import DEBUG
from scrapers import AdlerScraper, DegewoScraper, GewobagScraper
from properties import Identity
from util import log
import time
import yaml
import argparse
from termcolor import colored
import traceback
import random


if __name__ != "__main__":
    exit()

parser = argparse.ArgumentParser()
parser.add_argument("-d", action="store_true", help="Enable debug mode")
DEBUG_ENABLED = parser.parse_args().d

if DEBUG_ENABLED:
    print(colored("Debug mode is enabled", color="red", attrs=["bold"]))
    # load alternative config here

with open("data/config-prod.yml", "r") as config_file:
    CONFIG = yaml.safe_load(config_file)

SEEN_FILE_URL = "seen_properties.txt"
SLEEP_LEN = CONFIG["sleep-len"]
N_APPLICATIONS = CONFIG["n-applications"]  # applications per ad

scrapers = [
    GewobagScraper(CONFIG["gewobag-search-url"]),
    DegewoScraper(CONFIG["degewo-search-url"]),
    AdlerScraper(CONFIG["adler-search-url"]),
]

try:
    with open(SEEN_FILE_URL, "r") as f:
        seen_properties = [line.rstrip() for line in f.readlines()]
except IOError:
    seen_properties = []


def apply_to_property(property, use_fakes=True):
    start_time = time.time()

    # generate a list of real and fake identities to apply with:
    application_set = [
        Identity("Martin", "Hoffmann", "martin.hoffmann@charite.de"),
        Identity("Martin", "Hoffmann", "m.hoffmann@systemli.org"),
        Identity("Edwin", "Hoffmann", "edwinhoffmann49@t-online.de"),
        Identity("Martin", "Hoffmann", "martin.hoffmann@uni-potsdam.de"),
        Identity("Martin", "Hoffmann", "hoffmann47@uni-potsdam.de"),
    ]

    for i in range(N_APPLICATIONS):
        email = f"martin.hoffmann98+{i+1}@systemli.org"
        application_set.append(Identity("Martin", "Hoffmann", email))

        if not use_fakes:
            continue
        for _ in range(random.randint(0, 2)):
            application_set.append(Identity())  # add some fake identities

    # apply with the given identities:
    for id in application_set:
        status_code, status_text = property.apply(id)
        log(f"{id} {property.id} {status_code} {status_text}")
        time.sleep(random.randint(2, 5))

    delta = time.time() - start_time
    log(f"Sent {len(application_set)} applications in {delta:.1f}s.")


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
        f"{len(found_properties)} properties seen in total ({len(filtered_properties)} new)"
    )

    if DEBUG_ENABLED:
        print("\n".join([f"{p.title} {p.url}" for p in filtered_properties]))
        exit()

    for property in filtered_properties:
        seen_properties.append(property.url)
        with open(SEEN_FILE_URL, "a") as f:  # will create file if not exists
            f.write(f"{property.url}\n")

        log(f"Neues Angebot: {property}")
        apply_to_property(property, use_fakes=True)

    time.sleep(SLEEP_LEN)
