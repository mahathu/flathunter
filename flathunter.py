import pandas as pd
import traceback
import logging
import time
import yaml

from scrapers import AdlerScraper, DegewoScraper, GewobagScraper, CovivioScraper
from archive import Archive


# TODO: vllt wird config-dict gar nicht mehr gebraucht, sondern direkt z.b. self.sleep statt self.config["sleep-len"]
# TODO: filter-Funktion ggf. auslagern in eigene Klasse
class Flathunter:
    def __init__(
        self, config_path="config.yml", archive_path="seen_ads.csv", debug_enabled=False
    ):
        self.debug = debug_enabled
        self.config = self.load_config(config_path)
        self.archive = Archive(archive_path)
        # self.archive_path = archive_path
        # self.seen_ads_df = self.load_seen_ads(archive_path)
        self.scrapers = [
            AdlerScraper(self.config["adler-search-url"]),
            # CovivioScraper(self.config["covivio-search-url"]),
            # DegewoScraper(self.config["degewo-search-url"]),
            # GewobagScraper(self.config["gewobag-search-url"]),
        ]

        logging.info(f"App initialized. Debug: {self.debug}")

    def load_config(self, config_path):
        with open(config_path, "r") as config_file:
            return yaml.safe_load(config_file)

    def batch_apply(self, property, n_applications, use_fakes=True):
        if self.debug:
            logging.info(f"Not applying to {property} because debug mode is enabled.")
            return

        raise NotImplementedError

    def run_scrapers(self):
        found_properties = []

        # TODO: exceptions should probably be handled within the scrapers
        for scraper in self.scrapers:
            try:
                results = scraper.find_properties()
                found_properties.extend(results)
            except Exception:
                logging.error(f"Exception in {scraper}: {traceback.format_exc()}")

        new_properties = [
            p for p in found_properties if p.url not in self.archive._df["url"].values
        ]

        logging.info(f"Found {len(found_properties)} ads ({len(new_properties)} new).")
        return new_properties

    def process_new_properties(self, new_properties):
        for property in new_properties:
            if property.filter_status != "OK":
                logging.info(f"Skipping {property} because: {property.filter_status}")
                continue
            if property.company in ["covivio", "adler"]:
                logging.info(
                    f"Skipping {property} (not implemented {property.company})"
                )
                continue
            self.batch_apply(property, self.config["n-applications"], use_fakes=True)

    def run(self):
        logging.info(f"App is running 🚀")

        while True:
            new_properties = self.run_scrapers()

            if new_properties:
                self.archive.append(new_properties)
                self.process_new_properties(new_properties)

            logging.info(f"Sleeping for {self.config['sleep-len']} seconds.")
            time.sleep(self.config["sleep-len"])
