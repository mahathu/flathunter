import logging
import yaml

config = {}


def load_config(file_url):
    global config
    try:
        with open(file_url, "r") as config_file:
            config = yaml.safe_load(config_file)
            logging.info(f"Loaded config from {file_url}")

    except FileNotFoundError:
        logging.error(f"Config file not found: {file_url}")
        exit(1)

    except yaml.YAMLError as e:
        logging.error(f"Error parsing config file: {e}")
        exit(1)

    logging.info(f"Loaded config from config.yml")


def get_config():
    print(config)
    return config
