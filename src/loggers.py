import os
import sys
import logging.config

import colorama

LOGGING_LEVEL =  int(
    os.environ.get(
        "LOG_LEVEL", 
        logging.DEBUG if __debug__ else logging.WARNING
    )
) 
LOGFILE_MAXSIZE = int(
    os.environ.get(
        "LOGFILE_MAXSIZE",
        8*1024*1024
    )
)
LOGGS_PATH = os.environ["BSO_LOGS_PATH"]
DEFAULT_LOGGER_SETTINGS = {
    "handlers": ["console", "file"],
    "level": LOGGING_LEVEL,
    "propagate": False,
}


colorama.init()
class ColorFilter(logging.Filter):
    _d = {
        0: colorama.Fore.LIGHTBLACK_EX,
        10: colorama.Fore.LIGHTBLUE_EX,
        15: colorama.Back.YELLOW + colorama.Fore.BLACK,
        20: colorama.Fore.LIGHTWHITE_EX,
        30: colorama.Fore.LIGHTYELLOW_EX,
        40: colorama.Fore.LIGHTRED_EX,
        50: colorama.Back.LIGHTMAGENTA_EX,
        60: colorama.Style.BRIGHT + colorama.Back.LIGHTRED_EX
    }
    def filter(self, record: logging.LogRecord):
        setattr(record, "c", ColorFilter._d[record.levelno])
        setattr(record, "r", colorama.Style.RESET_ALL)
        return True


config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "colored_console": {
            "format": ("%(name)s  %(c)s %(levelname)-8s %(r)s %(asctime)s."
                       "%(msecs)d %(c)s%(message)s%(r)s"),
            "datefmt": "%s",
            "comment": "only for use with ColorFilter"
        },
        "file": {
            "format": "%(name)s %(levelname)s %(asctime)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "()": logging.StreamHandler,
            "stream": sys.stdout,
            "formatter": "colored_console",
            "filters": [ColorFilter()]
        },
        "file": {
            "()": logging.handlers.RotatingFileHandler,
            "filename": os.path.join(LOGGS_PATH, ".log"),  
            "maxBytes": LOGFILE_MAXSIZE,
            "backupCount": 8,
            "formatter": "file",
        },
    },
    "loggers": {
        "database": DEFAULT_LOGGER_SETTINGS,
        "blanks": DEFAULT_LOGGER_SETTINGS,
    },
    "root": {
        "level": logging.WARNING,
        "handlers": ["console",]
    }
}


logging.config.dictConfig(config)
