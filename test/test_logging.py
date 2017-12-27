# coding=utf-8
"""
Tests logging package
"""

import logging
import logging.handlers
from pathlib import Path

import pytest

from elib.custom_logging import CustomLoggingHandler, get_logger
from elib.custom_random import random_string


@pytest.fixture(scope='function')
def setup_logging(caplog):
    """Provides a logger and the caplog fixture"""
    logger = get_logger(logger_name=random_string(), console_level=logging.DEBUG)
    yield logger, caplog


# noinspection PyShadowingNames
def test_logger(setup_logging):
    logger, caplog = setup_logging
    assert isinstance(logger, logging.Logger)
    assert logger is logging.getLogger(logger.name)
    caplog.set_level(logging.DEBUG)
    logger.info('test_message_debug')
    assert 'test_message_debug' in caplog.text
    assert get_logger(logger.name) is logging.getLogger(logger.name)


# noinspection PyShadowingNames
def test_double_instantiation():
    first_logger = get_logger('test_logger')
    second_logger = get_logger('test_logger')
    assert first_logger is second_logger


# noinspection PyShadowingNames
@pytest.mark.parametrize('levels', [
    (logging.DEBUG, logging.INFO, 'debug'),
    (logging.INFO, logging.WARNING, 'info'),
    (logging.WARNING, logging.ERROR, 'warning'),
    (logging.ERROR, logging.CRITICAL, 'error'),
])
def test_logger_levels(setup_logging, levels):
    logger, caplog = setup_logging
    caplog.set_level(levels[1])
    out_func = getattr(logger, levels[2])
    out_func('test_message_debug')
    assert 'test_message_debug' not in caplog.text
    caplog.set_level(levels[0])
    out_func('test_message_debug')
    assert 'test_message_debug' in caplog.text


# noinspection PyShadowingNames
@pytest.mark.parametrize('level', ['debug', 'info', 'warning', 'error', 'critical'])
def test_logger_not_set(setup_logging, level):
    logger, caplog = setup_logging
    caplog.set_level(logging.NOTSET)
    out_func = getattr(logger, level)
    out_func('test_message_debug')
    assert 'test_message_debug' in caplog.text


def test_file_handler():
    log_file = Path('./log.file')
    assert not log_file.exists()
    logger = get_logger(random_string(), log_to_file=str(log_file))
    logger.warning('test')
    assert log_file.exists()
    assert 'test' in log_file.read_text()


def test_file_handler_levels():
    log_file = Path('./log.file')
    assert not log_file.exists()
    logger = get_logger(random_string(), log_to_file=str(log_file), file_level=logging.ERROR)
    logger.warning('test')
    assert log_file.exists()
    assert 'test' not in log_file.read_text()


def test_rotating_file_handler():
    log_file = Path('./log.file', )
    assert not log_file.exists()
    logger = get_logger(random_string(), log_to_file=str(log_file), rotate_logs=True)
    logger.warning('test')
    assert log_file.exists()
    assert 'test' in log_file.read_text()
    assert len(list(log_file.parent.glob('*'))) == 1
    for handler in logger.handlers:
        if isinstance(handler, logging.handlers.TimedRotatingFileHandler):
            handler.doRollover()
            assert len(list(log_file.parent.glob('*'))) == 2
            break
    else:
        assert logger.handlers is None
        raise LookupError('no rotating file handler found')


# noinspection PyShadowingNames
def test_custom_handler(setup_logging):
    logger, _ = setup_logging

    result = False

    def _callback(*_):
        nonlocal result
        result = True

    handler = CustomLoggingHandler('handler')
    handler.emit = _callback

    handler.register(logger)

    logger.info('test')
    assert result
