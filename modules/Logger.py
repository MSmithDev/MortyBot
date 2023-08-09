import logging
from termcolor import colored

# Define a custom log formatter
class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': 'blue',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'magenta'
    }

    def format(self, record):
        log_message = super(ColoredFormatter, self).format(record)
        return colored(log_message, self.COLORS.get(record.levelname))

def setup_logger(name: str, level: int):
    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create a file handler to write logs to a file
    file_handler = logging.FileHandler('MortyBot.log')
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))

    # Create a console handler to print logs to the console with colors
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(ColoredFormatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))


    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger