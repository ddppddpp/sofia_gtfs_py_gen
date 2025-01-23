"""
A module initializing the logging funtionality
"""
import logging

def logger():
    """Initialize the logging functionality"""
    logger_object = logging.getLogger(__name__)
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(
        "gtfs_gen.log", 
        mode="a",
        encoding="utf-8"
    )
    logger_object.setLevel("DEBUG")
    console_handler.setLevel("INFO")
    file_handler.setLevel("DEBUG")
    logger_object.addHandler(console_handler)
    logger_object.addHandler(file_handler)
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        style="%",
        datefmt="%Y-%m-%d %H:%M",
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    return logger_object
