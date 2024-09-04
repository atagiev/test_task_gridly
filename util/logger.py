import logging
import os
import sys
from logging import LoggerAdapter, Logger

ERROR_TEMPLATE = '\033[48;5;196m\033[37m{}\033[0m'
FORMAT_TEMPLATE = '%(levelname)-8s %(threadName)s --> %(message)s'


class LoggerConfig:
    level = os.environ.get('LOG_LEVEL', 'INFO')


class LevelFormatter(logging.Formatter):
    def __init__(self, fmt=None, level_fmts=None):
        self.levelFormatters = {}
        if level_fmts:
            for level, level_format in level_fmts.items():
                self.levelFormatters[level] = logging.Formatter(fmt=level_format)
        super().__init__(fmt=fmt)

    def format(self, record):
        if record.levelno in self.levelFormatters:
            return self.levelFormatters[record.levelno].format(record)

        return super(LevelFormatter, self).format(record)


def get_logger(name: str) -> logging.LoggerAdapter:
    loggers = Logger.manager.loggerDict
    if name in loggers:
        del loggers[name]
    log = logging.getLogger(name)
    logger_config = LoggerConfig()
    formatter = LevelFormatter(fmt=FORMAT_TEMPLATE, level_fmts={
        logging.ERROR: ERROR_TEMPLATE.format(FORMAT_TEMPLATE)
    })
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(formatter)
    log.setLevel(logger_config.level)
    log.addHandler(console_handler)

    return LoggerAdapter(log)


logger = get_logger('gridly_integration')
