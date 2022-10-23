from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
from typing import List


class Property(object):
    def __init__(self, company, address, title, url, id) -> None:
        self.company = company
        self.address = address
        self.title = title
        self.url = url
        self.id = id

    def __str__(self) -> str:
        return f"[{self.company.upper()}] {self.title} ({self.address})"

    def apply(self):
        pass


class Scraper(ABC):
    def __init__(self, url) -> None:
        self.url = url

    @abstractmethod
    def find_properties(self) -> List[Property]:
        pass

    # TODO: make a default function here that gets overwritten for adler, SUL etc
    # TODO: make property an object


class GewobagScraper(Scraper):
    def find_properties(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, "lxml")

        return [
            Property(
                company="gewobag",
                address=item.find("address").text.strip(),
                title=item.find("h3", {"class": "angebot-title"}).text.strip(),
                url=item.select("a.angebot-header")[0]["href"],
                id=item.select("a.angebot-header")[0]["href"]
                .split("/")[-2]
                .replace("-", "%2F"),
            )
            for item in soup.select(".filtered-mietangebote article")
        ]


class DegewoScraper(Scraper):
    # für den Link: Suche durchführen, im Netzwerk-Tab die URL des JSON-Requests kopieren.
    def find_properties(self):
        response = requests.get(self.url)
        immos = response.json()["immos"]

        return [
            Property(
                company="degewo",
                address=property["address"],
                title=property["headline"],
                url="https://immosuche.degewo.de" + property["property_path"],
                id=property["property_path"].split("/")[-1].replace("-", ".", 2),
            )
            for property in immos
        ]


class AdlerScraper(Scraper):
    # https://www.adler-group.com/suche/wohnung
    # für den richtigen Link Suche durchführen und "immoscoutgrabber" Link aus devtools kopieren, der
    # ein "geodata"-JSON-Objekt zurückschickt
    def find_properties(self):
        response = requests.get(self.url)
        properties = response.json()["geodata"]

        results = []
        for property in properties:
            try:
                addr = property["address"]
                prop_addr = (
                    f'{addr["street"]} {addr["houseNumber"]} ({addr["quarter"]})'
                )
            except KeyError:
                prop_addr = "Unknown address"

            results.append(
                Property(
                    company="adler",
                    address=prop_addr,
                    title=property["title"],
                    url=property["link"],
                    id=property["isid"],
                )
            )

        return results

    def apply_to_property(property_id):
        pass


class WBMScraper(Scraper):
    def find_properties(self):
        pass


class StadtUndLandScraper(Scraper):
    # Anfrage wie POST-Request an 'https://www.stadtundland.de/exposes/immo.{prop_id}.php'
    # dabei wird ein form-token mitgeschickt. das ist im HTML der seite enthalten
    # außerdem schickt SUL keine Bestätigungsmail, schwer zu überprüfen ob Anfrage erfolgreich
    # https://stackoverflow.com/a/70640134/2349901
    def find_properties(self):
        print("hi")


if __name__ == "__main__":
    s = StadtUndLandScraper("")
    s.find_properties()
