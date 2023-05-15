import pandas as pd
import logging


class Archive:
    def __init__(self, path) -> None:
        self.path = path
        try:
            self._df = pd.read_csv(path)
            logging.info(f"Loaded archive file {path} (n={len(self._df)}.)")

        except (FileNotFoundError, pd.errors.EmptyDataError):
            logging.info(f"Provided archive file {path} empty or does not exist.")
            self._df = pd.DataFrame(columns=["url"])

    def append(self, new_properties):
        new_ads_df = pd.DataFrame([p.as_dict() for p in new_properties])
        self._df = pd.concat([self._df, new_ads_df])

        # Write to file
        self._df.to_csv(self.path, index=False)
