import os
from datetime import datetime
import logging
import structlog

class CustomLogger:

    def __init__(self, log_dir="logs"):
        log_dir = os.path.join(os.getcwd(), log_dir)
        os.makedirs(log_dir, exist_ok=True)

        # Create a log file with the current timestamp
        log_file_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".log"
        self.log_file_path = os.path.join(log_dir, log_file_name)


    # Create a logger instance
    def get_logger(self, name=__file__):
        """Get a structured logger instance."""
        logger_name = os.path.basename(name)
        # configure logging for file (json format)
        file_handler = logging.FileHandler(self.log_file_path)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter("%(message)s")) # Raw json format

        # Configure logging for console output
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter("%(message)s")) # Raw json format

        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            handlers=[console_handler, file_handler]
        )

        # configure the structlog
        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
                structlog.processors.add_log_level,
                structlog.processors.EventRenamer(to="event"),
                structlog.processors.JSONRenderer()
            ],
            #context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            #wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True
        )
        return structlog.get_logger(logger_name)


if __name__ == "__main__":
    logger = CustomLogger()
    logger = logger.get_logger(__file__)
    logger.info("Custom logger initialized.")