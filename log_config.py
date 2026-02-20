import logging
import os
import sys

_configured = False


def get_logger(name):
    global _configured
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'run_log.txt')
    if not _configured:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
            handlers=[
                logging.FileHandler(log_path, mode='a', encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        _configured = True
    return logging.getLogger(name)
