import sys
import logging.config
import colorama


colorama.init()

class ColorFilter(logging.Filter):
    _d = {
        0: colorama.Fore.LIGHTBLACK_EX,
        10: colorama.Fore.LIGHTBLUE_EX,
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


LOGGING_LEVEL = logging.DEBUG if __debug__ else logging.WARNING

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
            "level": logging.DEBUG,
            "formatter": "colored_console",
            "filters": [ColorFilter()]
        },
        "file": {
            "()": logging.FileHandler,
            "filename": "logs/.log",
            "level": logging.DEBUG,
            "formatter": "file",
        },
    },
    "loggers": {
        "database": {
            "handlers": ["console", "file"],
            "level": LOGGING_LEVEL,
            "propagate": False,
        },
        "test": {
            "handlers": ["console", "file"],
            "level": LOGGING_LEVEL,
            "propagate": False,
        },
        "report_service": {
            "handlers": ["console", "file"],
            "level": LOGGING_LEVEL,
            "propagate": False,
        },
    },
    "root": {
        "level": logging.WARNING,
        "handlers": ["console",]
    }
}


logging.config.dictConfig(config)
