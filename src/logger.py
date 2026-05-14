import logging

_logger = None


def init_logger(log_path):
    global _logger
    _logger = logging.getLogger("eagle_mail")
    _logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))

    _logger.addHandler(file_handler)
    _logger.addHandler(console_handler)


def log_moved(mailbox, contact, subject, folder):
    _logger.info(f"MOVED   | {mailbox:<6} | {contact:<35} | {subject[:45]:<45} | -> {folder}")


def log_skipped(mailbox, contact, subject, reason):
    _logger.info(f"SKIPPED | {mailbox:<6} | {contact:<35} | {subject[:45]:<45} | Reason: {reason}")


def log_error(message):
    _logger.error(f"ERROR   | {message}")


def log_info(message):
    _logger.info(f"INFO    | {message}")
