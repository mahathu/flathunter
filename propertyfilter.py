from properties import Property


class PropertyFilter:
    def __init__(self, zip_whitelist, zip_blacklist, title_blacklist, min_sqm):
        self.zip_whitelist = zip_whitelist
        self.zip_blacklist = zip_blacklist
        self.title_blacklist = title_blacklist
        self.min_sqm = min_sqm

    def filter_property(self, property: Property) -> str:
        pass
