import argparse
from .core.utils import setup_logger
from .cli.repl import QCCRepl

logger = setup_logger()

def main():
    parser = argparse.ArgumentParser(
        description="Quantum Circuit Composer (QCC) - Universal Quantum Tool"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="QCC v0.1.0 (Phase 2)"
    )
    args = parser.parse_args()

    logger.info("QCC started successfully.")

    if len(vars(args)) == 0:
        repl = QCCRepl()
        repl.run()
    else:
        pass

if __name__ == "__main__":
    main()
