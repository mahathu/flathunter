import logging
from abc import ABC, abstractmethod
from typing import List
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from .properties import Property, AdlerProperty, WohnungsheldenProperty


class Scraper(ABC):
    def __repr__(self) -> str:
        # e.g. <GewobagScraper>
        return f"<{self.__class__.__name__}>"

    def __init__(self, url) -> None:
        self.url = url

    @abstractmethod
    def find_properties(self) -> List[Property]:
        pass


class GewobagScraper(Scraper):
    def find_properties(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, "lxml")

        props = soup.select(".filtered-mietangebote article")
        return [self.parse_listing(p) for p in props]

    def _parse_listing(self, property) -> WohnungsheldenProperty:
        addr = property.find("address").text.strip()
        zip = addr.split(", ")[1].split(" ")[0]
        url = property.select("table.angebot-info a")[0]["href"]
        id = url.split("/")[-2].replace("-", "%2F")

        try:
            sqm = float(
                property.select("tr.angebot-area td")[0]
                .text.split("| ")[-1]
                .split(" ")[0]
                .replace(",", ".")
            )
            rent = property.select("tr.angebot-kosten td")[0].text

        except (IndexError, ValueError) as e:
            logging.error(f"Error parsing sqm or rent on gewobag property: {e}")
            sqm = 1000  # when in doubt, put a really high square footage so applications are sent anyways
            rent = 0  # likewise for the

        return WohnungsheldenProperty(
            company="gewobag",
            address=addr,
            zip_code=zip,
            sqm=sqm,
            rent=rent,
            title=property.find("h3", {"class": "angebot-title"}).text.strip(),
            url=url,
            id=id,
        )


class DegewoScraper(Scraper):
    # To get the link, run a search query and copy the URL of the JSON request from Network Tools.
    def find_properties(self):
        response = requests.get(self.url)
        immos = response.json()["immos"]

        return [
            WohnungsheldenProperty(
                company="degewo",
                address=property["address"],
                zip_code=property["zipcode"],
                sqm=property["living_space"],
                rent=property["rent_cold"],
                title=property["headline"],
                url="https://immosuche.degewo.de" + property["property_path"],
                id=property["id"].replace("-", ".", 2),
            )
            for property in immos
        ]


class CovivioScraper(Scraper):
    # this will only parse the first results page.
    # page is passed as a URL parameter. TODO: recursively request pages until 400
    def find_properties(self):
        response = requests.get(self.url)

        return [
            WohnungsheldenProperty(
                company="covivio",
                address=property["adresse"],
                zip_code=property["adresse"].split()[-2],
                sqm=property["wohnflaeche"],
                rent=property["kaltmiete"],
                title=property["title"]["rendered"],
                url=property["link"],
                id=property["id"],
            )
            for property in response.json()
        ]


class AdlerScraper(Scraper):
    def find_properties(self):
        response = requests.get(self.url)
        props = response.json()["geodata"]

        return [self._parse_listing(property) for property in props]

    def _parse_listing(self, property):
        try:
            addr = property["address"]
            district = addr["quarter"].split("(")[0]
            prop_zipcode = addr["postcode"]
            prop_addr = (
                f'{addr["street"]} {addr["houseNumber"]}, {prop_zipcode} {district}'
            )

        except KeyError:
            prop_addr = "Unknown address"
            prop_zipcode = "00000"

        return AdlerProperty(
            company="adler",
            address=prop_addr,
            zip_code=prop_zipcode,
            sqm=property["livingSpace"],
            rent=property["price"],
            title=property["title"],
            url=property["link"],
            id=property["isid"],
        )


class WBMScraper(Scraper):
    def find_properties(self):
        raise NotImplementedError


class StadtUndLandScraper(Scraper):
    # Anfrage wie POST-Request an 'https://www.stadtundland.de/exposes/immo.{prop_id}.php'
    # dabei wird ein form-token mitgeschickt. das ist im HTML der seite enthalten
    # außerdem schickt SUL keine Bestätigungsmail, schwer zu überprüfen ob Anfrage erfolgreich
    # https://stackoverflow.com/a/70640134/2349901
    def find_properties(self):
        raise NotImplementedError


def init_scraper(url):
    # TODO: don't mix data and code
    scraper_mapping = {
        "adler-group.com": AdlerScraper,
        "covivio.immo": CovivioScraper,
        "immosuche.degewo.de": DegewoScraper,
        "gewobag.de": GewobagScraper,
    }

    base_url = urlparse(url).netloc.removeprefix("www.")
    return scraper_mapping[base_url](url)
