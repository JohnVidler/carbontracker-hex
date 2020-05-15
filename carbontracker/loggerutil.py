import logging
import os
import sys
import pathlib
import datetime


def convert_to_timestring(seconds, add_milliseconds=True):
    return str(datetime.timedelta(seconds=seconds)).split(".")[0]


class TrackerFormatter(logging.Formatter):
    converter = datetime.datetime.fromtimestamp

    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime("%Y-%m-%d %H:%M:%S")
            s = "%s" % t
        return s


class Logger:
    def __init__(self, log_dir=None, verbose=0):
        self.logger, self.logger_output, self.logger_err = self._setup(
            log_dir=log_dir)
        self._log_initial_info()
        self.verbose = verbose
        self.msg_prepend = "CarbonTracker: "

    def _setup(self, log_dir=None):
        logger = logging.getLogger("carbontracker")
        logger_err = logging.getLogger("carbontracker.err")
        logger_output = logging.getLogger("carbontracker.output")
        # Disable output logging from propagating to parent loggers.
        logger.propagate = False
        logger.setLevel(logging.DEBUG)
        logger_output.propagate = False
        logger_output.setLevel(logging.DEBUG)
        logger_err.propagate = False
        logger_err.setLevel(logging.DEBUG)

        # Add output logging to console.
        ch = logging.StreamHandler(stream=sys.stdout)
        c_formatter = logging.Formatter("{message}", style="{")
        ch.setLevel(logging.INFO)
        ch.setFormatter(c_formatter)
        logger_output.addHandler(ch)

        if log_dir is not None:
            # Create logging directory if it does not exist.
            pathlib.Path(log_dir).mkdir(parents=True, exist_ok=True)

            # ISO8601 format YYYY-MM-DDThh:mmZ.
            date_format = "%Y-%m-%dT%H:%MZ"
            date = datetime.datetime.now().strftime(date_format)

            f_formatter = TrackerFormatter(fmt="%(asctime)s - %(message)s")

            # Add output logging to file.
            fh = logging.FileHandler(
                f"{log_dir}/{date}_carbontracker_output.log")
            fh.setLevel(logging.INFO)
            fh.setFormatter(f_formatter)
            logger_output.addHandler(fh)

            # Add standard logging to file.
            f = logging.FileHandler(f"{log_dir}/{date}_carbontracker.log")
            f.setLevel(logging.DEBUG)
            f.setFormatter(f_formatter)
            logger.addHandler(f)

            # Add error logging to file.
            err_formatter = logging.Formatter(
                "{asctime} - {threadName} - {levelname} - {message}",
                style="{")
            f_err = logging.FileHandler(
                f"{log_dir}/{date}_carbontracker_err.log", delay=True)
            f_err.setLevel(logging.DEBUG)
            f_err.setFormatter(err_formatter)
            logger_err.addHandler(f_err)

        return logger, logger_output, logger_err

    def _log_initial_info(self):
        here = os.path.abspath(os.path.dirname(__file__))
        about = {}
        with open(os.path.join(here, "__version__.py")) as f:
            exec(f.read(), about)
        self.info(f"{about['__title__']} version {about['__version__']}")

    def output(self, msg, verbose_level=0):
        if self.verbose >= verbose_level:
            self.logger_output.info(self.msg_prepend + msg)

    def info(self, msg):
        self.logger.info(msg)

    def err_debug(self, msg):
        self.logger_err.debug(msg)

    def err_info(self, msg):
        self.logger_err.info(msg)

    def err_warn(self, msg):
        self.logger_err.warn(msg)

    def err_critical(self, msg):
        self.logger_err.critical(msg)
