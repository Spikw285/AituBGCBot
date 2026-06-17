# logger.py
import logging
import re
from pythonjsonlogger import jsonlogger


def _anonymize(text: str) -> str:
    """
    Обезличивает чувствительные данные перед записью в лог.
    Telegram ID частично маскируется, имена скрываются полностью.
    """
    # Telegram ID: 123456789 → 123***789
    text = re.sub(
        r'("?tg_id"?\s*[:=]\s*)(\d{3})\d+(\d{3})',
        r'\1\2***\3',
        text
    )
    # Имя пользователя: "Иван Петров" → "Ива*** ***ов"
    text = re.sub(
        r'("?full_name"?\s*[:=]\s*"?)(\w{3})\w+\s(\w*\w{2})(\w+"?)',
        r'\1\2*** ***\3\4',
        text
    )
    return text


class AnonymizingFormatter(logging.Formatter):
    """Форматтер который прогоняет каждое сообщение через _anonymize."""

    def format(self, record: logging.LogRecord) -> str:
        formatted = super().format(record)
        return _anonymize(formatted)


def setup_logging(debug: bool = False) -> None:
    """
    Настраивает логирование для всего приложения.

    debug=True  → уровень DEBUG, видны все SQL-запросы и FSM-переходы
    debug=False → уровень INFO, только важные события

    Использование:
        from logger import setup_logging
        setup_logging(debug=settings.DEBUG)
    """
    level = logging.DEBUG if debug else logging.INFO

    # Формат строки лога
    formatter = AnonymizingFormatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Вывод в консоль
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Вывод в файл (удобно смотреть историю)
    file_handler = logging.FileHandler("bot.log", encoding="utf-8")
    file_handler.setFormatter(formatter)

    logging.basicConfig(level=level, handlers=[console_handler, file_handler])

    # Подавляем слишком verbose логи от библиотек
    logging.getLogger("aiogram").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if debug else logging.WARNING
    )