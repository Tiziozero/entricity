import logging

# Create a custom logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set the logger level to capture all levels of logs

# Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('client.log')

# Set levels for handlers if needed
c_handler.setLevel(logging.DEBUG)  # Set to DEBUG to capture all logs for the console
f_handler.setLevel(logging.DEBUG)  # Set to DEBUG to capture all logs for the file

# Create formatters and add it to handlers
c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
f_format = logging.Formatter('%(asctime)s - %(message)s')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)

"""
def log(*args, **kwargs) -> None:
    logger.log(*args, **kwargs)
"""
log = logger.info
warn = logger.warning
err = logger.error

# Example usage
log("This is an info message")
warn("This is a warning message")
err("This is an error message")

