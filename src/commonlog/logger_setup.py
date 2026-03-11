import logging
import os
import sys
import uuid
from logging.handlers import RotatingFileHandler

__all__ = ['single_logger']

program_unique_id = uuid.uuid4()

if os.environ.get('UNITTESTING'):
    unit_testing = 'UNIT_TESTING.'
else:
    unit_testing = ''

bc_format_str = unit_testing + "{}.{}.{}"


class BreadcrumbFilter(logging.Filter):
    """Provides %(breadcrumbs) field for the logger formatter.

    Th breadcrumbs field returns module.funcName.lineno as a single string.
     example:
        formatters={
        'console_format': {'format':
                           '%(asctime)-30s %(breadcrumbs)-35s %(levelname)s: %(message)s'}
                   }
       self.logger.debug('handle_accept() -> %s', client_info[1])
        2020-11-08 14:04:40,561        echo_server03.handle_accept.24      DEBUG: handle_accept() -> ('127.0.0.1',
        49515)
    """

    def filter(self, record):
        record.breadcrumbs = bc_format_str.format(record.module, record.funcName, record.lineno)
        return True


def set_up_logger(lg=None, console_log=True, file_log=None, **kwargs):
    """Instantiate a logger with presets.

    By default, logs to the console and a file in the current directory.

    :param file_log: str, path to the file to write the log to. Default './logfile.log'.
    :param console_log: bool, whether to write to the console. Default True.
    :return: the logger
    """

    if kwargs.get('suppress_prints') is not True:
        # in case of old print/pprint statements while running without a console; redirect them to devnull to get rid
        # of them; this prevents them from slowing the program where they cannot even be seen
        if 'PROMPT' not in os.environ:
            nullfile = open(os.devnull, 'w')
            sys.stdout = nullfile
            sys.stderr = nullfile

    on_dev_node = kwargs.get('ON_DEV_NODE')

    # set up the logging
    if lg is None:
        lg = logging.getLogger('common_logger')
    base_log_level = logging.DEBUG if on_dev_node else logging.INFO
    lg.setLevel(base_log_level)

    if console_log:
        # console logger
        c_handler = logging.StreamHandler()
        c_handler.setLevel(base_log_level)
        c_format = logging.Formatter('%(asctime)-30s %(breadcrumbs)-45s %(levelname)s: %(message)s')
        c_handler.setFormatter(c_format)
        c_handler.addFilter(BreadcrumbFilter())
        lg.addHandler(c_handler)

    if file_log:
        # file logger
        f_handler = RotatingFileHandler(file_log, maxBytes=2000000, backupCount=1)
        f_handler.setLevel(logging.DEBUG)
        # f_string = '"%(asctime)s","%(name)s", "%(breadcrumbs)s","%(funcName)s","%(lineno)d","%(levelname)s","%(message)s"'
        f_string = ('"%(asctime)s",'
                    '"%(name)s",'
                    f'"{str(program_unique_id)[:8]}",'
                    '"%(process)d",'
                    '"%(breadcrumbs)s",'
                    '"%(funcName)s",'
                    '"%(lineno)d",'
                    '"%(levelname)s",'
                    '"%(message)s"'
                    )

        class CustomFormatter(logging.Formatter):
            def format(self, record):
                try:
                    record.msg = record.msg.replace('"', '\'')
                except AttributeError:
                    pass  # the msg is not always a string, if it's not, then there are no quotes
                return logging.Formatter.format(self, record)

        f_format = CustomFormatter(f_string)

        f_format = logging.Formatter(f_string)
        f_handler.addFilter(BreadcrumbFilter())
        f_handler.setFormatter(f_format)

        # Add handlers to the logger

        lg.addHandler(f_handler)

    def handle_exception(exc_type, exc_value, exc_traceback):
        """Log unhandled exceptions."""

        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        lg.critical('Uncaught exception', exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = handle_exception

    return lg


# protect against multiple loggers from importing in multiple files
def single_logger(*args, **kwargs):
    """Get the root logger if it exists with handlers, else a logger using setup_logger using any arguments."""
    return set_up_logger(*args, **kwargs) if not logging.getLogger().hasHandlers() else logging.getLogger()


if __name__ == '__main__':
    lg = single_logger('test_log.log')
    pass

    # protect against multiple loggers from importing in multiple files
    lg = set_up_logger() if not logging.getLogger().hasHandlers() else logging.getLogger()

    # if ON_DEV_NODE:  # suppress log spam from dependencies
    #     logging.getLogger('requests').setLevel(logging.INFO)
    #     logging.getLogger('urllib3').setLevel(logging.INFO)
    #
    # else:
    #     # looging at log file data
    #     import pandas as pd
    #
    #     column_names = ['tstamp', 'program', 'uid', 'pid', 'breadcrumbs', 'callable', 'line#', 'level',
    #                     'message']  # + [f'col{n}' for n in range(8)]
    #     ldf = pd.read_csv('../mahlo_popup.log', names=column_names)
    #     col_name = 'tstamp'
    #     ldf = ldf[len(ldf) - 5000::]
    #     ldf[col_name] = pd.to_datetime(ldf[col_name])
    #
    #     ldf = ldf[ldf['tstamp'] > '2022-03-18']
