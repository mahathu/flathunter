import logging
import pandas as pd


class Archive:
    def __init__(self, path) -> None:
        self.path = path
        try:
            self._df = pd.read_csv(path)
            logging.info(f"Loaded archive file {path} (n={len(self._df)}).")

        except (FileNotFoundError, pd.errors.EmptyDataError):
            logging.warning(f"Provided archive file {path} empty or does not exist.")
            self._df = pd.DataFrame(columns=["url"])

    def __contains__(self, url):
        return url in self._df["url"].values

    def append(self, property):
        new_ads_df = pd.DataFrame([property.as_dict()])
        self._df = pd.concat([self._df, new_ads_df])

        self._df.to_csv(self.path, index=False)  # Write to file
