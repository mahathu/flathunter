from scrapers import AdlerScraper, DegewoScraper, GewobagScraper, CovivioScraper
from properties import Identity
from util import log
import time
import yaml
import argparse
import pandas as pd
from termcolor import colored
import traceback
import random


if __name__ != "__main__":
    exit()

CONFIG_PATH = "data/config-narrow.yml"
parser = argparse.ArgumentParser()
parser.add_argument("-d", action="store_true", help="Enable debug mode")
DEBUG_ENABLED = parser.parse_args().d

if DEBUG_ENABLED:
    # config_path = "data/config-debug.yml"
    print(colored("Debug mode is enabled", color="red", attrs=["bold"]))

with open(CONFIG_PATH, "r") as config_file:
    CONFIG = yaml.safe_load(config_file)
    log(f"Loaded config from {CONFIG_PATH}")

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
    application_set = []

    for i in range(N_APPLICATIONS):
        email = f"martin.hoffmann98+{i+1}@systemli.org"
        application_set.append(Identity("Martin", "Hoffmann", email))

        if not use_fakes:
            continue
        for _ in range(random.randint(0, 3)):
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

    log(
        f"{len(found_properties)} ads currently online (new: {len(new_properties)}, total: {len(seen_ads_df)})"
    )

    for property in new_properties:
        if property.filter_status != "OK":
            log(
                f"Skipping {property} because: {property.filter_status}"
            )
            continue

        if property.company == "covivio":
            log(f"Skipping {property} (not implemented)")
            continue

        batch_apply(property, use_fakes=True)

    log(f"Sleeping for {SLEEP_LEN} seconds.")
    time.sleep(SLEEP_LEN)
