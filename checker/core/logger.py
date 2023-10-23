import logging

LOGGING = {
    "format": "%(levelname)-8s [%(asctime)s] "
    "%(name)s.%(funcName)s:%(lineno)d %(message)s",
    "level": logging.INFO,
    "handlers": [logging.StreamHandler()],
}
