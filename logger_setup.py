import logging
import sys

from logging.handlers import RotatingFileHandler


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
        record.breadcrumbs = "{}.{}.{}".format(record.module, record.funcName, record.lineno)
        return True


def setup_logger(file_log='logfile.log', console_log=True):
    """Instantiate a logger with presets.

    By default logs to the console and a file in the current directory.

    :param file_log: str, path to the file to write the log to. Default './logfile.log'.
    :param console_log: bool, whether to write to the console. Default True.
    :return: the logger
    """

    # set up the logging
    logr = logging.getLogger()
    logr.setLevel(logging.DEBUG)

    if console_log:
        # console logger
        c_handler = logging.StreamHandler()
        c_handler.setLevel(logging.DEBUG)
        c_format = logging.Formatter('%(asctime)-30s %(breadcrumbs)-45s %(levelname)s: %(message)s')
        c_handler.setFormatter(c_format)
        c_handler.addFilter(BreadcrumbFilter())
        logr.addHandler(c_handler)

    if file_log:
        # file logger
        f_handler = RotatingFileHandler(file_log, maxBytes=2000000)
        f_handler.setLevel(logging.DEBUG)
        f_string = '"%(asctime)s","%(name)s", "%(breadcrumbs)s","%(funcName)s","%(lineno)d","%(levelname)s","%(message)s"'
        f_format = logging.Formatter(f_string)
        f_handler.addFilter(BreadcrumbFilter())
        f_handler.setFormatter(f_format)

    # Add handlers to the logger

    logr.addHandler(f_handler)

    def handle_exception(exc_type, exc_value, exc_traceback):
        """Log unhandled exceptions."""

        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logr.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = handle_exception

    return logr


# protect against multiple loggers from importing in multiple files
def single_logger(*args, **kwargs):
    """Get a the root logger if it exists with handlers, else a logger using setup_logger using any arguments."""
    return setup_logger(*args, **kwargs) if not logging.getLogger().hasHandlers() else logging.getLogger()


if __name__ == '__main__':
    lg = single_logger('test_log.log')
    pass