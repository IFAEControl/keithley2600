import logging.handlers

# Defined here since it is imported in other pyvisa modules
BASE_NAME = 'k2600'
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def log_to_screen(level=logging.DEBUG) -> None:
    log_to_stream(None, level)  # sys.stderr by default


def log_to_stream(stream_output, level=logging.DEBUG) -> None:
    logger.setLevel(level)
    ch = logging.StreamHandler(stream_output)
    ch.setLevel(level)
    ch.setFormatter(formatter)

    logger.addHandler(ch)


def log_add_file_handler(file_path, level=logging.DEBUG):
    fh = logging.handlers.RotatingFileHandler(filename=file_path, maxBytes=5 * 1024 * 1024, backupCount=5)
    fh.setLevel(level=level)
    fh.setFormatter(formatter)
    logger.addHandler(fh)


__version__ = "unknown"

" It is a list of strings defining what symbols in a module willbe exported when"
" from <module> import * is used on the module."

__all__ = [
    "logger",
    "log_to_screen",
    "log_to_stream",
    "log_add_file_handler",
]
