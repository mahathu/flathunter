from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
from typing import List
from properties import Property, AdlerProperty, WHProperty
from util import log


class Scraper(ABC):
    def __init__(self, url) -> None:
        self.url = url

    @abstractmethod
    def find_properties(self) -> List[Property]:
        pass


class GewobagScraper(Scraper):
    def find_properties(self):
        # response = requests.get(self.url)
        response = requests.get(
            "https://www.gewobag.de/fuer-mieter-und-mietinteressenten/mietangebote/?bezirke_all=1&bezirke%5B%5D=charlottenburg-wilmersdorf&bezirke%5B%5D=charlottenburg-wilmersdorf-charlottenburg&bezirke%5B%5D=friedrichshain-kreuzberg&bezirke%5B%5D=friedrichshain-kreuzberg-friedrichshain&bezirke%5B%5D=friedrichshain-kreuzberg-kreuzberg&bezirke%5B%5D=lichtenberg&bezirke%5B%5D=lichtenberg-alt-hohenschoenhausen&bezirke%5B%5D=lichtenberg-falkenberg&bezirke%5B%5D=lichtenberg-fennpfuhl&bezirke%5B%5D=marzahn-hellersdorf&bezirke%5B%5D=marzahn-hellersdorf-marzahn&bezirke%5B%5D=mitte&bezirke%5B%5D=mitte-gesundbrunnen&bezirke%5B%5D=mitte-moabit&bezirke%5B%5D=neukoelln&bezirke%5B%5D=neukoelln-britz&bezirke%5B%5D=neukoelln-buckow&bezirke%5B%5D=neukoelln-rudow&bezirke%5B%5D=pankow&bezirke%5B%5D=pankow-prenzlauer-berg&bezirke%5B%5D=reinickendorf&bezirke%5B%5D=reinickendorf-hermsdorf&bezirke%5B%5D=reinickendorf-tegel&bezirke%5B%5D=reinickendorf-waidmannslust&bezirke%5B%5D=spandau&bezirke%5B%5D=spandau-hakenfelde&bezirke%5B%5D=spandau-haselhorst&bezirke%5B%5D=spandau-staaken&bezirke%5B%5D=spandau-wilhelmstadt&bezirke%5B%5D=steglitz-zehlendorf&bezirke%5B%5D=steglitz-zehlendorf-lichterfelde&bezirke%5B%5D=steglitz-zehlendorf-steglitz&bezirke%5B%5D=tempelhof-schoeneberg&bezirke%5B%5D=tempelhof-schoeneberg-lichtenrade&bezirke%5B%5D=tempelhof-schoeneberg-mariendorf&bezirke%5B%5D=tempelhof-schoeneberg-marienfelde&bezirke%5B%5D=tempelhof-schoeneberg-schoeneberg&bezirke%5B%5D=treptow-koepenick&bezirke%5B%5D=treptow-koepenick-altglienicke&bezirke%5B%5D=treptow-koepenick-niederschoeneweide&nutzungsarten%5B%5D=wohnung&gesamtmiete_von=&gesamtmiete_bis=&gesamtflaeche_von=&gesamtflaeche_bis=&zimmer_von=&zimmer_bis=&sort-by=recent"
        )
        soup = BeautifulSoup(response.text, "lxml")

        results = []
        for property in soup.select(".filtered-mietangebote article"):
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
                rent = 0
            except (IndexError, ValueError) as e:
                log(f"EXCEPTION parsing sqm or rent on gewobag property: {e}")
                sqm = 1000  # when in doubt, just apply to it anyways
                rent = 0
                
            results.append(
                WHProperty(
                    company="gewobag",
                    address=addr,
                    zip_code=zip,
                    sqm=sqm,
                    rent=0,
                    title=property.find("h3", {"class": "angebot-title"}).text.strip(),
                    url=url,
                    id=id,
                )
            )

        return results


class DegewoScraper(Scraper):
    # für den Link: Suche durchführen, im Netzwerk-Tab die URL des JSON-Requests kopieren.
    def find_properties(self):
        response = requests.get(self.url)
        immos = response.json()["immos"]

        return [
            WHProperty(
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
            WHProperty(
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
        properties = response.json()["geodata"]

        results = []
        for property in properties:
            try:
                addr = property["address"]
                prop_addr = (
                    f'{addr["street"]} {addr["houseNumber"]} ({addr["quarter"]})'
                )
                prop_zipcode = addr["postcode"]

            except KeyError:
                prop_addr = "Unknown address"
                prop_zipcode = "00000"

            results.append(
                AdlerProperty(
                    company="adler",
                    address=prop_addr,
                    zip_code=prop_zipcode,
                    sqm=property["livingSpace"],
                    rent=property["price"],
                    title=property["title"],
                    url=property["link"],
                    id=property["isid"],
                )
            )

        return results


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
