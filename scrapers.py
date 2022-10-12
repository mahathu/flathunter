from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup


class Scraper(ABC):
    def __init__(self, url) -> None:
        self.url = url

    @abstractmethod
    def get_items():
        pass


class GewobagScraper(Scraper):
    def get_items(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, "lxml")

        results = [
            {
                "company": "gewobag",
                "address": item.find("address").text.strip(),
                "title": item.find("h3", {"class": "angebot-title"}).text.strip(),
                "url": item.select("a.angebot-header")[0]["href"],
                "id": item.select("a.angebot-header")[0]["href"]
                .split("/")[-2]
                .replace("-", "%2F"),
            }
            for item in soup.select(".filtered-mietangebote article")
        ]

        return results


class DegewoScraper(Scraper):
    # für den Link: Suche durchführen, im Netzwerk-Tab die URL des JSON-Requests kopieren.
    def get_items(self):
        response = requests.get(self.url)
        immos = response.json()["immos"]

        results = [
            {
                "company": "degewo",
                "address": property["address"],
                "title": property["headline"],
                "url": "https://immosuche.degewo.de" + property["property_path"],
                "id": property["property_path"].split("/")[-1].replace("-", ".", 2),
            }
            for property in immos
        ]

        return results


class AdlerScraper(Scraper):
    # https://www.adler-group.com/suche/wohnung
    # für den richtigen Link Suche durchführen und "immoscoutgrabber" Link kopieren, der
    # ein "geodata"-JSON-Objekt zurückschickt
    def get_items(self):
        response = requests.get(self.url)
        properties = response.json()["geodata"]

        results = [
            {
                "company": "adler",
                "address": " ".join(
                    v if isinstance(v, str) else ""
                    for v in property["address"].values()
                ),
                "title": property["title"],
                "url": property["link"],
                "id": property["link"].split("?")[0].split("/")[-1],
            }
            for property in properties
        ]

        return results

    def apply_to_property(property_id):
        pass

    # für die Bewerbung wird folgender request gesendet, das alle Angaben in der URL kodiert
    # https://www.adler-group.com/index.php?tx_immoscoutgrabber_pi2%5B__referrer%5D%5B%40extension%5D=ImmoscoutGrabber&tx_immoscoutgrabber_pi2%5B__referrer%5D%5B%40controller%5D=ShowObjects&tx_immoscoutgrabber_pi2%5B__referrer%5D%5B%40action%5D=displaySingleExpose&tx_immoscoutgrabber_pi2%5B__referrer%5D%5Barguments%5D=YToxOntzOjI6ImlkIjtzOjk6IjEzNTgwODk4MiI7fQ%3D%3D19444e96a05922d4039645c65aa7df411736b0fb&tx_immoscoutgrabber_pi2%5B__referrer%5D%5B%40request%5D=%7B%22%40extension%22%3A%22ImmoscoutGrabber%22%2C%22%40controller%22%3A%22ShowObjects%22%2C%22%40action%22%3A%22displaySingleExpose%22%7D1ef78d7bfc1912570b7737fc000249e80b5eb13c&tx_immoscoutgrabber_pi2%5B__trustedProperties%5D=%7B%22is_mandatory%22%3A%5B1%2C1%2C1%2C1%5D%2C%22contact_firstname%22%3A1%2C%22contact_lastname%22%3A1%2C%22contact_phone%22%3A1%2C%22contact_email%22%3A1%2C%22contact_message%22%3A1%2C%22gdpr-ack%22%3A1%2C%22action%22%3A1%2C%22exposeid%22%3A1%7D5b8f74aea4017d8ee8af7d2f3f7a4f1030d56040&tx_immoscoutgrabber_pi2%5Bcontact_salutation%5D=mr&tx_immoscoutgrabber_pi2%5Bis_mandatory%5D%5B%5D=contact_salutation&tx_immoscoutgrabber_pi2%5Bcontact_firstname%5D=as&tx_immoscoutgrabber_pi2%5Bis_mandatory%5D%5B%5D=contact_firstname&tx_immoscoutgrabber_pi2%5Bcontact_lastname%5D=asd&tx_immoscoutgrabber_pi2%5Bis_mandatory%5D%5B%5D=contact_lastname&tx_immoscoutgrabber_pi2%5Bcontact_phone%5D=&tx_immoscoutgrabber_pi2%5Bcontact_email%5D=ads%40de.de&tx_immoscoutgrabber_pi2%5Bis_mandatory%5D%5B%5D=contact_email&tx_immoscoutgrabber_pi2%5Bcontact_message%5D=&tx_immoscoutgrabber_pi2%5Bgdpr-ack%5D=&tx_immoscoutgrabber_pi2%5Bgdpr-ack%5D=true&tx_immoscoutgrabber_pi2%5Baction%5D=submitForm&tx_immoscoutgrabber_pi2%5Bexposeid%5D=135808982&type=4276906
    # Server antwortet: {success: true, errors: []} (mails werden nicht auf Duplikate gecheckt.....)


class HowogeScraper(Scraper):
    # Howoge verwendet ein merkwürdiges system, Anfragen werden per POST request geschickt
    # ggf später drum kümmern
    def get_items(self):
        pass


class StadtUndLandScraper(Scraper):
    # bei stadt und land müssen Anfragen per POST request gemacht werden, außerdem
    # muss ein serverseitig generiertes token mitgeschickt werden -> scrapy?
    # außerdem schickt SUL keine Bestätigungsmail, schwer zu überprüfen ob Anfrage erfolgreich
    # https://stackoverflow.com/a/70640134/2349901
    def get_items(self):
        pass
