from scrapers import DegewoScraper, GewobagScraper
from send_requests import apply_to_property
import time
import yaml

with open("config.yml", "r") as config_file:
    CONFIG = yaml.safe_load(config_file)

DISTRICT_BLACKLIST = ["Rudow", "Waidmannslust", "Staaken", "Marzahn", "Lichtenrade"]
TITLE_BLACKLIST = [
    "Single",
    "Senior",
    "Selbstrenovierer",
    "mit WBS",
    "im Grünen",
    "WBS mit besonderem Wohnbedarf erforderlich",
    "WBS mit Besonderem Wohnbedarf erforderlich",
    "WBS erforderlich",
    "WBS-fähigem",
    "Rollstuhlfahrer",
    "WBS nötig",
]
SEEN_FILE_URL = "seen_properties.txt"
SLEEP_LEN = CONFIG["sleep-len"]
N_APPLICATIONS = CONFIG["n-applications"]  # applications per ad
EMAIL_SET = [f"martin.hoffmann98+{i+1}@systemli.org" for i in range(N_APPLICATIONS)]

scrapers = [
    GewobagScraper(CONFIG["gewobag-search-url"]),
    DegewoScraper(CONFIG["degewo-search-url"]),
]


def result_filter(result):
    """returns true if result is wanted and false otherwise"""
    if result["url"] in seen_properties:
        return False

    if any([word in result["title"] for word in TITLE_BLACKLIST]):
        return False

    if any([district in result["address"] for district in DISTRICT_BLACKLIST]):
        return False

    return True


def log(line):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {line}", flush=True)


if __name__ == "__main__":
    try:
        with open(SEEN_FILE_URL, "r") as f:
            seen_properties = [line.rstrip() for line in f.readlines()]
    except IOError:
        seen_properties = []

    while True:
        try:
            for scraper in scrapers:
                for property in filter(result_filter, scraper.get_items()):
                    seen_properties.append(property["url"])
                    log(
                        f"Neues Angebot gefunden: {property['title']}: {property['address']}"
                    )

                    apply_to_property(property["company"], property["id"], EMAIL_SET)

                    with open(
                        SEEN_FILE_URL, "a"
                    ) as f:  # will create file if not exists
                        f.write(f"{property['url']}\n")

        except Exception as e:  # this shouldn't catch KeyboardInterrupts I think
            log(f"Exception: {e}")

        log(f"Sleeping for {SLEEP_LEN} seconds.")
        time.sleep(SLEEP_LEN)
