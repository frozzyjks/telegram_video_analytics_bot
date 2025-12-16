import re
from datetime import date, time
from dateutil import parser as date_parser

RU_MONTHS = {
    "январь": 1, "января": 1, "январе": 1,
    "февраль": 2, "февраля": 2, "феврале": 2,
    "март": 3, "марта": 3, "марте": 3,
    "апрель": 4, "апреля": 4, "апреле": 4,
    "май": 5, "мая": 5, "мае": 5,
    "июнь": 6, "июня": 6, "июне": 6,
    "июль": 7, "июля": 7, "июле": 7,
    "август": 8, "августа": 8, "августе": 8,
    "сентябрь": 9, "сентября": 9, "сентябре": 9,
    "октябрь": 10, "октября": 10, "октябре": 10,
    "ноябрь": 11, "ноября": 11, "ноябре": 11,
    "декабрь": 12, "декабря": 12, "декабре": 12
}


def extract_time_interval(text: str) -> tuple[time | None, time | None]:
    match = re.search(r"с (\d{1,2}:\d{2}) до (\d{1,2}:\d{2})", text)
    if not match:
        return None, None
    start_str, end_str = match.groups()
    return time.fromisoformat(start_str), time.fromisoformat(end_str)

def parse_time(text: str) -> time | None:
    match = re.search(r"(\d{1,2}):(\d{2})", text)
    if match:
        h, m = int(match.group(1)), int(match.group(2))
        return time(h, m)
    return None


def extract_time_range(text: str) -> tuple[time | None, time | None]:
    times = re.findall(r"(\d{1,2}:\d{2})", text)
    if len(times) == 2:
        return parse_time(times[0]), parse_time(times[1])
    return None, None


def extract_month_year(text: str) -> tuple[int, int] | None:
    """Ищет месяц и год в тексте типа 'в июне 2025 года'"""
    match = re.search(r"в\s+([а-яё]+)\s+(\d{4})", text)
    if match:
        month_str, year_str = match.groups()
        month = RU_MONTHS.get(month_str.lower())
        if month:
            return month, int(year_str)
    return None

def extract_creator_id(text: str) -> str | None:
    match = re.search(r"id\s+([0-9a-f]{32})", text)
    return match.group(1) if match else None

def extract_threshold(text: str) -> int | None:
    match = re.search(r"(?:больше|более)\s+([\d\s]+)\s+просмотр", text)
    if match:
        return int(match.group(1).replace(" ", ""))
    return None

def parse_ru_date(text: str) -> date | None:
    match = re.search(r"(\d{1,2})\s+([а-яё]+)\s+(\d{4})", text)
    if not match:
        return None
    day = int(match.group(1))
    month = RU_MONTHS.get(match.group(2))
    year = int(match.group(3))
    if month:
        return date(year, month, day)
    return None

def extract_date_range(text: str) -> tuple[date | None, date | None]:
    dates = re.findall(r"\d{1,2}\s+[а-яё]+\s+\d{4}", text)
    if len(dates) == 2:
        return parse_ru_date(dates[0]), parse_ru_date(dates[1])
    return None, None

def extract_single_date(text: str) -> date | None:
    return parse_ru_date(text)


def parse_query(text: str) -> dict:
    text_lower = text.lower()
    creator_id = extract_creator_id(text_lower)
    threshold = extract_threshold(text_lower)
    date_from, date_to = extract_date_range(text_lower)
    start_time, end_time = extract_time_interval(text_lower)
    single_date = extract_single_date(text_lower)

    month_year = extract_month_year(text_lower)


    if "разных креаторов" in text_lower and "просмотр" in text_lower:
        threshold = extract_threshold(text_lower)
        return {
            "query_type": "CREATORS_WITH_VIDEOS_VIEWS_GT",
            "threshold": threshold
        }

    if "на сколько просмотров суммарно выросли все видео" in text_lower and creator_id and start_time and end_time:
        return {
            "query_type": "SUM_DELTA_VIEWS_BY_INTERVAL",
            "creator_id": creator_id,
            "date": single_date,
            "start_time": start_time,
            "end_time": end_time,
        }


    if month_year and ("суммарное количество просмотров" in text_lower or "набрали" in text_lower):
        month, year = month_year
        return {
            "query_type": "SUM_VIEWS_BY_MONTH",
            "month": month,
            "year": year,
        }

    if "сколько всего видео" in text_lower:
        return {
            "query_type": "TOTAL_VIDEOS",
            "creator_id": None,
            "date_from": None,
            "date_to": None,
            "threshold": None
        }

    if creator_id and date_from and date_to:
        return {
            "query_type": "CREATOR_VIDEOS_BY_PERIOD",
            "creator_id": creator_id,
            "date_from": date_from,
            "date_to": date_to,
            "threshold": None
        }

    if threshold is not None and "просмотр" in text_lower:
        return {
            "query_type": "VIDEOS_VIEWS_GT",
            "creator_id": creator_id,
            "date_from": None,
            "date_to": None,
            "threshold": threshold
        }

    if "на сколько просмотров" in text_lower:
        return {
            "query_type": "SUM_DELTA_VIEWS_BY_DAY",
            "creator_id": None,
            "date_from": extract_single_date(text_lower),
            "date_to": None,
            "threshold": None
        }

    if "сколько" in text_lower and "видео" in text_lower and ("получили" in text_lower or "получали" in text_lower):
        return {
            "query_type": "VIDEOS_WITH_DELTA_BY_DAY",
            "creator_id": None,
            "date_from": extract_single_date(text_lower),
            "date_to": None,
            "threshold": None
        }

    if "замер" in text_lower and ("отрицательн" in text_lower or "стало меньше" in text_lower) and "просмотр" in text_lower:
        return {
            "query_type": "NEGATIVE_VIEWS_DELTAS_COUNT",
            "creator_id": None,
            "date_from": None,
            "date_to": None,
            "threshold": None
        }

    if creator_id and "разных календарных днях" in text_lower and "публиковал" in text_lower:
        month_year = re.search(r"([а-яё]+)\s+(\d{4})", text_lower)
        if month_year:
            month_str, year_str = month_year.groups()
            month = RU_MONTHS.get(month_str)
            year = int(year_str)
            if month:
                return {
                    "query_type": "CREATOR_ACTIVE_DAYS_IN_MONTH",
                    "creator_id": creator_id,
                    "month": month,
                    "year": year
                }

    raise ValueError("Не удалось распознать запрос")
