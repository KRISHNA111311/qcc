import logging
from pathlib import Path

def setup_logger(name: str = "qcc") -> logging.Logger:
    log_dir = Path.home() / ".qcc" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "qcc.log"

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)

    return logger
