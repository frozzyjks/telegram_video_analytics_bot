import re
from datetime import date


RU_MONTHS = {
    "января": 1,
    "февраля": 2,
    "марта": 3,
    "апреля": 4,
    "мая": 5,
    "июня": 6,
    "июля": 7,
    "августа": 8,
    "сентября": 9,
    "октября": 10,
    "ноября": 11,
    "декабря": 12,
}


def extract_creator_id(text: str) -> str | None:
    match = re.search(r"id\s+([0-9a-fA-F]{32})", text)
    return match.group(1) if match else None


def extract_threshold(text: str) -> int | None:
    match = re.search(r"(?:больше|более)\s+([\d\s]+)\s+просмотр", text)
    if not match:
        return None
    return int(match.group(1).replace(" ", ""))


def parse_ru_date(text: str) -> date | None:
    match = re.search(r"(\d{1,2})\s+([а-яё]+)\s+(\d{4})", text)
    if not match:
        return None

    day = int(match.group(1))
    month = RU_MONTHS.get(match.group(2))
    year = int(match.group(3))

    if not month:
        return None

    return date(year, month, day)


def extract_date_range(text: str) -> tuple[date | None, date | None]:
    dates = re.findall(r"\d{1,2}\s+[а-яё]+\s+\d{4}", text)
    if len(dates) != 2:
        return None, None

    return parse_ru_date(dates[0]), parse_ru_date(dates[1])


def extract_single_date(text: str) -> date | None:
    return parse_ru_date(text)


# -----------------------------
# main parser
# -----------------------------

def parse_query(text: str) -> dict:
    text = text.lower()

    creator_id = extract_creator_id(text)
    threshold = extract_threshold(text)
    date_from, date_to = extract_date_range(text)

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
    if creator_id and date_from and date_to:
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
        return {
            "query_type": "SUM_DELTA_VIEWS_BY_DAY",
            "creator_id": None,
            "date_from": extract_single_date(text),
            "date_to": None,
            "threshold": None,
        }

    # 5. сколько разных видео получили/получали новые просмотры
    if (
        "сколько" in text
        and "видео" in text
        and ("получили" in text or "получали" in text)
    ):
        return {
            "query_type": "VIDEOS_WITH_DELTA_BY_DAY",
            "creator_id": None,
            "date_from": extract_single_date(text),
            "date_to": None,
            "threshold": None,
        }

    raise ValueError("Не удалось распознать запрос")
