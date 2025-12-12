import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger(
    name: str = "app",
    log_dir: str = "logs",
    filename: str = "app.log",
    level: int = logging.INFO,
    max_bytes: int = 2_000_000,  # 2 MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Sets up a rotating file logger and returns the logger instance.
    """

    # Ensure directory exists
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Full log file path
    file_path = log_path / filename

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False  # Prevent duplicate logs if root logger is set

    # Avoid adding multiple handlers if called twice
    if not logger.handlers:

        # File handler with rotation
        file_handler = RotatingFileHandler(
            file_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8"
        )

        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(formatter)

        # Stream handler (console)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


# ---- Helper function to log messages anywhere ----

def log_message(message: str, level: str = "info", logger_name: str = "app"):
    """
    Log a message using the configured logger.
    level: 'info', 'warning', 'error', 'debug', 'critical'
    """
    try:
        logger = logging.getLogger(logger_name)
        
        # Validar se o logger tem handlers configurados
        if not logger.handlers and logger_name != "app":
            # Tentar configurar o logger automaticamente se não estiver configurado
            setup_logger(name=logger_name, filename=f"{logger_name}.log")
            logger = logging.getLogger(logger_name) # Recarregar logger configurado

        match level.lower():
            case "info":
                logger.info(message)
            case "warning":
                logger.warning(message)
            case "error":
                logger.error(message)
            case "debug":
                logger.debug(message)
            case "critical":
                logger.critical(message)
            case _:
                logger.info(message)
    except Exception as e:
        logging.error(f"Erro ao fazer log de mensagem: {e}", exc_info=True)
