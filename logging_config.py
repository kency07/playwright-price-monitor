import logging


def setup_logging():
    if logging.getLogger().hasHandlers():
        return

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s: %(message)s",
        handlers=[
            logging.FileHandler("data/alerts.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
