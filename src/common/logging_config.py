import logging, os, sys

# root logger
def setup_logging() -> None:
    """ Call once at application startup """

    # read log level from env, default is Info
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    # defining what each log line looks like
    formatter = logging.Formatter(
        fmt = "date - %(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # handler where logs should go  - sdout here
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # root logger - all child logger bubbles up to this
    root = logging.getLogger()
    root.setLevel(level)

    # don't add duplicate handlers if called twice
    if not root.handlers:
        root.addHandler(handler)
    
    # Silence noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("litellm").setLevel(logging.WARNING)


# test block
if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Logging works!")
    logger.warning("This is a warning")
    logger.error("This is error")