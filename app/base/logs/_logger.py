import logging

from .records import CacheMessageLogRecord

__all__ = ['logger']

logging.setLogRecordFactory(CacheMessageLogRecord)

logger = logging.getLogger('api')

_critical = logger.critical
logger.critical = lambda *args, **kws: _critical(  # type:ignore
    *args, **kws, exc_info=True
)
