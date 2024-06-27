import logging

DEFAULT_NAME = "Default"


def create_logger(name=DEFAULT_NAME):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname).1s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    ch.setFormatter(formatter)

    logger.addHandler(ch)

    return logger


logger = create_logger()
