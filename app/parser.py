import re
from datetime import date
from dateutil import parser as date_parser

def extract_creator_id(text: str) -> str | None:
    """
    Извлекает creator_id из текста:
    '... с id aca1061a9d324ecf8c3fa2bb32d7be63 ...'
    """
    match = re.search(r"id\s+([0-9a-fA-F]{32})", text)
    if match:
        return match.group(1)
    return None


def extract_threshold(text: str) -> int | None:
    match = re.search(
        r"(?:больше|более)\s+([\d\s]+)\s+просмотр",
        text
    )
    if match:
        number = match.group(1).replace(" ", "")
        return int(number)
    return None


def extract_single_date(text: str) -> date | None:
    """
    Извлекает одну дату:
    '28 ноября 2025'
    """
    try:
        return date_parser.parse(text, fuzzy=True, dayfirst=True).date()
    except Exception:
        return None


def extract_date_range(text: str) -> tuple[date | None, date | None]:
    """
    Извлекает диапазон дат:
    'с 1 ноября 2025 по 5 ноября 2025'
    """
    match = re.search(r"с (.+?) по (.+)", text)
    if not match:
        return None, None

    try:
        date_from = date_parser.parse(match.group(1), dayfirst=True).date()
        date_to = date_parser.parse(match.group(2), dayfirst=True).date()
        return date_from, date_to
    except Exception:
        return None, None


# -----------------------------
# main parser
# -----------------------------

def parse_query(text: str) -> dict:
    text = text.lower()

    creator_id = extract_creator_id(text)
    threshold = extract_threshold(text)

    # 1. сколько всего видео
    if "сколько всего видео" in text:
        return {
            "query_type": "TOTAL_VIDEOS",
            "creator_id": None,
            "date_from": None,
            "date_to": None,
            "threshold": None,
        }

    # 2. видео креатора за период
    if creator_id and "вышло" in text:
        date_from, date_to = extract_date_range(text)
        return {
            "query_type": "CREATOR_VIDEOS_BY_PERIOD",
            "creator_id": creator_id,
            "date_from": date_from,
            "date_to": date_to,
            "threshold": None,
        }

    # 3. видео с просмотрами больше X
    if threshold is not None and "просмотр" in text:
        return {
            "query_type": "VIDEOS_VIEWS_GT",
            "creator_id": creator_id,
            "date_from": None,
            "date_to": None,
            "threshold": threshold,
        }

    # 4. суммарный прирост просмотров за день
    if "на сколько просмотров" in text:
        single_date = extract_single_date(text)
        return {
            "query_type": "SUM_DELTA_VIEWS_BY_DAY",
            "creator_id": None,
            "date_from": single_date,
            "date_to": None,
            "threshold": None,
        }

    # 5. сколько видео получили новые просмотры
    if "сколько разных видео" in text:
        single_date = extract_single_date(text)
        return {
            "query_type": "VIDEOS_WITH_DELTA_BY_DAY",
            "creator_id": None,
            "date_from": single_date,
            "date_to": None,
            "threshold": None,
        }

    raise ValueError("Не удалось распознать запрос")
