import logging as _logging
import logging.handlers as _handlers

import config

_logging.basicConfig(level=_logging.DEBUG)
_logger = _logging.root
_logger.setLevel(_logging.DEBUG)
_handler = _handlers.TimedRotatingFileHandler(
    config.log_path, 'H', 24, 7)
_handler.setFormatter(_logging.Formatter(
    '[%(asctime)s] %(levelname)s %(lineno)d %(message)s'))
_logger.addHandler(_handler)

debug = _logger.debug
info = _logger.info
warning = _logger.warning
error = _logger.error
critical = _logger.critical
