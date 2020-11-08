"""Provides logging to console and a csv formatted file."""

import logging
from logging.config import dictConfig


class BreadcrumbFilter(logging.Filter):
    """Provides %(breadcrumbs) field for the logger formatter.

    Th breadcrumbs field returns module.funcName.lineno as a single string.
     example:
        formatters={
        'console_format': {'format':
                           '%(asctime)-30s %(breadcrumbs)-35s %(levelname)s: %(message)s'}
                   }
       self.logger.debug('handle_accept() -> %s', client_info[1])
        2020-11-08 14:04:40,561        echo_server03.handle_accept.24      DEBUG: handle_accept() -> ('127.0.0.1', 49515)
    """
    def filter(self, record):
        record.breadcrumbs = "{}.{}.{}".format(record.module, record.funcName, record.lineno)
        return True


base_logging_config = dict(
    version=1,
    filters={},
    formatters={},
    handlers={},
    root={},

)

file_logging_config = dict(
    version=1,
    filters={
        'column_filter': {
            '()': BreadcrumbFilter
        }
    },
    formatters={'log_file_format':
                {'format': '"%(asctime)s","%(breadcrumbs)s","%(funcName)s","%(lineno)d","%(levelname)s","%(message)s"'}
              },
    handlers={'rotating_csv_file_log_handler': {
            'level': 'DEBUG',
            'formatter': 'log_file_format',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'debug.log',
            'mode': 'a',
            'maxBytes': 1048576,
            'backupCount': 10}
    },
    root={
        'handlers': ['rotating_csv_file_log_handler'],
        'level': logging.DEBUG,
    },

)

console_logging_config = dict(
    version=1,
    filters={
        'column_filter': {
            '()': BreadcrumbFilter
        }
    },
    formatters={
        'console_format': {'format':
                           '%(asctime)-30s %(breadcrumbs)-45s %(levelname)s: %(message)s'}
    },
    handlers={
        'console_log_handler': {
                                'class': 'logging.StreamHandler',
                                'formatter': 'console_format',
                                'level': logging.DEBUG,
                                'filters': ['column_filter']}
    },
    root={
        'handlers': ['console_log_handler'],
        'level': logging.DEBUG,
    },
)

logging_config = base_logging_config
configs_to_use = []

# comment out/uncomment to add remove configs here
##########################################
configs_to_use += [console_logging_config]
# configs_to_use += [file_logging_config]
##########################################

# if everything is commented out, use the builtin basicConfig
if len(configs_to_use) == 0:
    logging.basicConfig()
else:
    for cfg_dct in configs_to_use:
        for l_key, l_val in console_logging_config.items():
            if l_key in logging_config.keys() and isinstance(l_val, dict):
                logging_config[l_key].update(l_val)
    logging.config.dictConfig(logging_config)

lg = logging.getLogger()

# test the logger
if __name__ == '__main__':
    lg.debug('often makes a very good meal of {}'.format('visiting tourists'))
