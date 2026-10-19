import logging

LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s tenant=%(tenant_id)s %(message)s"


def setup_logging(level: str) -> None:
    handler = logging.StreamHandler()
    # Logs from libraries have no tenant_id, so give them "-" instead of crashing.
    handler.setFormatter(logging.Formatter(LOG_FORMAT, defaults={"tenant_id": "-"}))
    logging.basicConfig(level=level, handlers=[handler], force=True)


def get_logger(name: str, tenant_id: str) -> logging.LoggerAdapter:
    return logging.LoggerAdapter(logging.getLogger(name), {"tenant_id": tenant_id})
