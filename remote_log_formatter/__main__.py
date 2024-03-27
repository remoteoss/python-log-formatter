from remote_log_formatter import get_logger, setup_logging

setup_logging(json=False)
logger = get_logger(__package__)
logger.info("foo")
