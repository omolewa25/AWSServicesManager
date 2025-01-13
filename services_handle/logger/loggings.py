import logging
import os


# Define a custom logging module
class Logger:
    def __init__(self, log_file='app.log', log_level=logging.DEBUG):
        """
        Initializes the logger with the desired log file and log level.
        :param log_file: Path to the log file
        :param log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)

        # Create a formatter
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(log_format)

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)

        # Add handlers to logger
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def get_logger(self):
        """
        Returns the logger instance.
        """
        return self.logger

    def log_debug(self, message):
        self.logger.debug(message)

    def log_info(self, message):
        self.logger.info(message)

    def log_warning(self, message):
        self.logger.warning(message)

    def log_error(self, message):
        self.logger.error(message)

    def log_exception(self, exception):
        """
        Log exception with traceback details.
        :param exception: The exception instance
        """
        self.logger.exception(exception)

    def log_critical(self, message):
        self.logger.critical(message)
