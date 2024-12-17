import logging


def setup_logging(verbosity: int):
    """
    Configure logging based on verbosity level.

    Args:
        verbosity (int): Verbosity level.
    """
    level = logging.WARNING  # Default level
    if verbosity == 1:
        level = logging.INFO
    elif verbosity >= 2:
        level = logging.DEBUG

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
