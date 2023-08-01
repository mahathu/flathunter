from termcolor import colored

from .properties import Property


class PropertyFilter:
    def __init__(self, zip_whitelist, zip_blacklist, title_blacklist, min_sqm) -> None:
        self.zip_whitelist = zip_whitelist
        self.zip_blacklist = zip_blacklist
        self.title_blacklist = title_blacklist
        self.min_sqm = min_sqm

    def filter(self, property: Property) -> str:
        if any(
            [word.lower() in property.title.lower() for word in self.title_blacklist]
        ):
            return "TITLE_BLACKLISTED"

        if self._wbs_required(property):
            return "WBS_REQUIRED"

        if not any([property.zip_code.startswith(str(p)) for p in self.zip_whitelist]):
            return "ZIP_NOT_WHITELISTED"

        if any([property.zip_code.startswith(str(p)) for p in self.zip_blacklist]):
            return "ZIP_BLACKLISTED"

        if property.sqm < self.min_sqm:
            return "TOO_SMALL"

        return "OK"

    def _wbs_required(self, property: Property) -> bool:
        """Tries to determine if a property requires a WBS
        (Wohnberechtigungsschein) based on it's title.

        Args:
            property (Property): The property to check.
        """
        title = property.title.lower()

        return any(w in title for w in ["wbs", "wohnberechtigungsschein"]) and not any(
            w in title for w in ["nicht", "kein", "ohne"]
        )


if __name__ == "__main__":
    f = PropertyFilter([101, 102, 104, 133], [1045], ["Senior"], 40)

    for zip_code in [10409, 10100, 10247, 13350]:
        p = Property("", "", str(zip_code), 100, "", "", "", "")
        assert f.filter(p) == "OK"

    for zip_code in [10303, 10456]:  # (1) wrong prefix (2) blacklisted
        p = Property("", "", str(zip_code), 100, "", "", "", "")
        assert f.filter(p) != "OK"

    for title in ["kein WBS erforderlich", "WBS nicht erforderlich", "ohne WBS", ""]:
        p = Property("", "", "10409", 100, 0, title, "", "")
        assert f.filter(p) == "OK"

    for title in [
        "für Senioren",  # title blacklist
        "im Erdgeschoss, WBS 100 erforderlich",
        "nur mit WBS",
        "WBS",
        "WBS zwingend erforderlich",
        "Mieter mit WBS-fähigem Einkommen",
    ]:
        p = Property("", "", "10409", 100, 0, title, "", "")
        assert f.filter(p) != "OK"

    # test square footage:
    assert f.filter(Property("", "", "10409", 70, "", "", "", "")) == "OK"
    assert f.filter(Property("", "", "10409", 35, "", "", "", "")) == "TOO_SMALL"
    print(colored("All tests passed!", "green"))
