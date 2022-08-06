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


# if __name__ == '__main__':
#     s = StadtUndLandScraper('https://www.stadtundland.de/Wohnungssuche/Wohnungssuche.php?form=stadtundland-expose-search-1.form&sp%3AroomsFrom%5B%5D=&sp%3AroomsTo%5B%5D=&sp%3ArentPriceFrom%5B%5D=&sp%3ArentPriceTo%5B%5D=&sp%3AareaFrom%5B%5D=&sp%3AareaTo%5B%5D=&sp%3Afeature%5B%5D=__last__&action=submit')
#     s.get_items()
