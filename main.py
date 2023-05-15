import argparse
import logging
import random
import sys
import time
import traceback

import pandas as pd
from termcolor import colored
import yaml

from scrapers import AdlerScraper, DegewoScraper, GewobagScraper, CovivioScraper
from properties import Identity


if __name__ != "__main__":
    exit()


logging.basicConfig(
    filename="logfile.log",
    encoding="utf-8",
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%m-%d-%Y %H:%M:%S",
)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


parser = argparse.ArgumentParser()
parser.add_argument(
    "-d", action="store_true", help="Enable debug mode (don't send applications)"
)
parser.add_argument("-c", "--config", help="Path to config file")

args = parser.parse_args()
DEBUG_ENABLED = args.d
CONFIG_PATH = args.config or "config.yml"

if DEBUG_ENABLED:
    logging.getLogger().setLevel(logging.DEBUG)
logging.debug("Debug mode is enabled")


with open(CONFIG_PATH, "r") as config_file:
    CONFIG = yaml.safe_load(config_file)
    logging.info(f"Loaded config from {CONFIG_PATH}")


SLEEP_LEN = CONFIG["sleep-len"]
N_APPLICATIONS = CONFIG["n-applications"]  # applications per ad

scrapers = [
    GewobagScraper(CONFIG["gewobag-search-url"]),
    DegewoScraper(CONFIG["degewo-search-url"]),
    AdlerScraper(CONFIG["adler-search-url"]),
    CovivioScraper(CONFIG["covivio-search-url"]),
]


seen_ads_df = pd.read_csv("data/seen_ads.csv")


def batch_apply(property, use_fakes=True):
    start_time = time.time()

    # generate a list of real and fake identities to apply with:
    application_set = [
        Identity("Martin", "Hoffmann", "m.hoffmann@systemli.org"),
        Identity("Martin", "Hoffmann", "m.hoffmann+92@systemli.org"),
        Identity("Martin", "Hoffmann", "m.hoffmann+berlin@systemli.org"),
    ]

    for i in range(N_APPLICATIONS):
        email = f"martin.hoffmann98+{i+1}@systemli.org"
        application_set.append(Identity("Martin", "Hoffmann", email))

        if not use_fakes:
            continue
        for _ in range(random.randint(0, 3)):
            application_set.append(Identity())  # add some fake identities inbetween

    # apply with the given identities:
    for id in application_set:
        status_code, status_text = property.apply(id)
        logging.debug(f"{id} {property.id} {status_code} {status_text}")
        time.sleep(random.randint(2, 5))

    delta = time.time() - start_time
    logging.info(f"Sent {len(application_set)} applications in {delta:.1f}s.")


while True:
    found_properties = []

    for scraper in scrapers:
        try:
            found_properties.extend(scraper.find_properties())
        except Exception as e:
            logging.info(traceback.format_exc())

    new_properties = [
        p for p in found_properties if p.url not in seen_ads_df["url"].values
    ]

    if DEBUG_ENABLED:
        print(f"The following {len(new_properties)} new properties were found:")
        for p in new_properties:
            print(p)
        exit()

    seen_ads_df = seen_ads_df.append(
        [p.as_dict() for p in new_properties], ignore_index=True
    )
    seen_ads_df.to_csv("data/seen_ads.csv", index=False)

    logging.info(
        f"{len(found_properties)} ads found online (new: {len(new_properties)}, total: {len(seen_ads_df)})"
    )

    for property in new_properties:
        if property.filter_status != "OK":
            logging.info(f"Skipping {property} because: {property.filter_status}")
            continue

        if property.company in ["covivio", "adler"]:
            logging.info(f"Skipping {property} (not implemented {property.company})")
            continue

        batch_apply(property, use_fakes=True)

    logging.info(f"Sleeping for {SLEEP_LEN} seconds.")
    time.sleep(SLEEP_LEN)
