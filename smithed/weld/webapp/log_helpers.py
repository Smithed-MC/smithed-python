import logging
from io import StringIO

logging.basicConfig(format="%(levelname)-8s %(message)s", level=logging.INFO)


def init_logger():
    stream = StringIO()
    console = logging.StreamHandler(stream)
    console.setFormatter(logging.Formatter("%(levelname)-12s %(message)s"))
    weld_logger = logging.getLogger("weld")
    weld_logger.addHandler(console)
    weld_logger.setLevel(logging.INFO)

    return stream
