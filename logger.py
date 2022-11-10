import os
import logging
from logging.handlers import TimedRotatingFileHandler


def get_logger(name: str, filename: str, when: str = 'W0') -> logging.Logger:

    if 'logs' not in os.listdir():
        os.mkdir('logs')

    log_format = logging.Formatter("%(asctime)s %(levelname)s %(name)s.%(funcName)s %(message)s")
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = TimedRotatingFileHandler(f"logs/{filename}.log", when, encoding='cp1251')
    handler.setFormatter(log_format)
    logger.addHandler(handler)
    return logger
