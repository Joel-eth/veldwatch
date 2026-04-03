import json
import logging

from veldwatch.logger import TRACE, EventLogger, StructuredFormatter, get_logger


def test_get_logger_returns_logger():
    logger = get_logger("test-logger-1", structured=False)
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test-logger-1"


def test_get_logger_idempotent():
    logger1 = get_logger("test-logger-2")
    logger2 = get_logger("test-logger-2")
    assert logger1 is logger2


def test_structured_formatter():
    fmt = StructuredFormatter()
    record = logging.LogRecord(
        name="test", level=logging.INFO, pathname="",
        lineno=0, msg="hello world", args=(), exc_info=None,
    )
    output = fmt.format(record)
    parsed = json.loads(output)
    assert parsed["message"] == "hello world"
    assert parsed["level"] == "INFO"
    assert "timestamp" in parsed


def test_structured_formatter_with_extra():
    fmt = StructuredFormatter()
    record = logging.LogRecord(
        name="test", level=logging.INFO, pathname="",
        lineno=0, msg="event", args=(), exc_info=None,
    )
    record.structured = {"run_id": "r1", "tokens": 150}  # type: ignore[attr-defined]
    output = fmt.format(record)
    parsed = json.loads(output)
    assert parsed["data"]["run_id"] == "r1"
    assert parsed["data"]["tokens"] == 150


def test_event_logger_info(capsys):
    logger = get_logger("test-event-info", level="INFO")
    el = EventLogger(logger)
    el.info("run started", run_id="r1")
    captured = capsys.readouterr()
    parsed = json.loads(captured.out.strip())
    assert parsed["message"] == "run started"
    assert parsed["data"]["run_id"] == "r1"


def test_event_logger_trace_level_suppressed(capsys):
    logger = get_logger("test-event-trace", level="INFO")
    el = EventLogger(logger)
    el.trace("very low level detail")
    captured = capsys.readouterr()
    # TRACE (5) is below INFO (20), should not appear
    assert captured.out == ""


def test_trace_level_constant():
    assert TRACE == 5
    assert logging.getLevelName(TRACE) == "TRACE"


def test_get_logger_file_sink(tmp_path):
    log_file = tmp_path / "test.log"
    logger = get_logger("test-file-sink", file_path=log_file)
    logger.info("file log test")

    content = log_file.read_text()
    parsed = json.loads(content.strip())
    assert parsed["message"] == "file log test"
