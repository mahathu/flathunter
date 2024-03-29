import argparse
import locale
import logging
import sys

from flathunter import Flathunter


def setup_logging():
    logging.basicConfig(
        filename="logfile.log",
        encoding="utf-8",
        level=logging.INFO,
        format="[%(asctime)s] %(message)s",
        datefmt="%m-%d-%Y %H:%M:%S",
    )
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Enable debug mode (don't send applications and don't save ads to archive)",
    )
    parser.add_argument(
        "-c", "--config", default="config.yml", help="Path to config file"
    )
    parser.add_argument(
        "-a", "--archive", default="seen_ads.csv", help="Path to archive file"
    )
    parser.add_argument("-s", "--server", action="store_true", help="Run web frontend")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging()
    locale.setlocale(
        locale.LC_TIME, "de_DE"
    )  # Set locale to Germany to properly parse date strings
    app = Flathunter(
        config_path=args.config, archive_path=args.archive, debug_enabled=args.debug
    )
    app.run()
