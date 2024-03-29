import pandas as pd
import traceback
import logging
import time
import yaml

from lib.scrapers import init_scraper
from lib.archive import Archive
from lib.propertyfilter import PropertyFilter
from lib.properties import Property


class Flathunter:
    def __init__(
        self, config_path="config.yml", archive_path="seen_ads.csv", debug_enabled=False
    ):
        self.debug = debug_enabled
        self.config = self.load_config(config_path)
        self.scrapers = [init_scraper(url) for url in self.config["search-urls"]]
        self.filter = PropertyFilter(
            zip_whitelist=self.config["zip-prefixes-whitelist"],
            zip_blacklist=self.config["zip-prefixes-blacklist"],
            title_blacklist=self.config["title-blacklist"],
            min_sqm=self.config["min-sqm"],
        )
        self.archive = Archive(archive_path)

        # TODO: Remove hardcoded reference to secrets.yml
        with open("secrets.yml", "r") as secrets_file:
            secrets = yaml.safe_load(secrets_file)
            self.proxies = {
                "http": secrets["proxy-url"],
                "https": secrets["proxy-url"],
            }

        log_str = f"App initialized with {len(self.scrapers)} scraper{'s' if len(self.scrapers) != 1 else ''}. Debug: {self.debug}"
        logging.info(log_str)

    def load_config(self, config_path: str) -> dict:
        with open(config_path, "r") as config_file:
            return yaml.safe_load(config_file)

    def schedule_applications(self, property: Property, n_applications: int) -> None:
        if self.debug:
            logging.info(f"Not applying to {property} because debug=True")
            return

        raise NotImplementedError

    def run_scrapers(self) -> list[Property]:
        found_properties = []

        for scraper in self.scrapers:
            try:
                results = scraper.find_properties()
                found_properties.extend(results)
            except Exception:
                logging.error(f"Exception in {scraper}: {traceback.format_exc()}")

        return found_properties

    def process_property(self, property: Property) -> None:
        property.filter_status = self.filter.filter(property)
        self.archive.append(property)

        if property.filter_status != "OK":
            logging.info(f"Skipping {property}: {property.filter_status}")
            return

        if property.company in ["covivio", "adler"]:
            logging.info(f"Skipping {property} (not implemented)")
            return

        self.schedule_applications(property, self.config["n-applications"])

    def run(self) -> None:
        """Main loop of the app.

        Running this function will search for and apply to new properties automatically.
        """
        logging.info(f"App is running 🚀")

        while True:
            found_properties = self.run_scrapers()
            new_properties = [p for p in found_properties if p.url not in self.archive]

            logging.info(
                f"Found {len(found_properties)} ads ({len(new_properties)} new)."
            )

            for property in new_properties:
                self.process_property(property)

            if self.debug or self.config["sleep-len"] < 0:
                return

            logging.info(f"Sleeping for {self.config['sleep-len']} seconds.")
            time.sleep(self.config["sleep-len"])
