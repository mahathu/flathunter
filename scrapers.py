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
        soup = BeautifulSoup(response.text, 'lxml')

        results = [
            {
                'company': 'gewobag',
                'address': item.find('address').text.strip(),
                'title': item.find('h3', {'class': 'angebot-title'}).text.strip(),
                'url': item.select('a.angebot-header')[0]['href'],
                'id': item.select('a.angebot-header')[0]['href'].split('/')[-2].replace('-', '%2F')
            }
            for item in soup.select('.filtered-mietangebote article')
        ]

        return results


class DegewoScraper(Scraper):
    def get_items(self):
        response = requests.get(self.url)
        immos = response.json()['immos']

        results = [
            {
                'company': 'degewo',
                'address': property['address'],
                'title': property['headline'],
                'url': 'https://immosuche.degewo.de' + property['property_path'],
                'id': property['property_path'].split('/')[-1].replace('-', '.', 2)
            }
            for property in immos
        ]

        return results
