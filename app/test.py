from parser import parse_query
from queries import (
    total_videos,
    creator_videos_by_period,
    videos_views_gt,
    sum_delta_views_by_day,
    videos_with_delta_by_day,
    count_negative_views_deltas,
    sum_views_by_month,
)

test_queries = [
    "Сколько всего видео есть в системе?",
    "Сколько видео у креатора с id 8b76e572635b400c9052286a56176e03 вышло с 1 ноября 2025 по 5 ноября 2025 включительно?",
    "Сколько видео у креатора с id aca1061a9d324ecf8c3fa2bb32d7be63 набрали больше 10 000 просмотров по итоговой статистике?",
    "На сколько просмотров в сумме выросли все видео 28 ноября 2025?",
    "Сколько разных видео получали новые просмотры 27 ноября 2025?",
    "Сколько всего есть замеров статистики (по всем видео), в которых число просмотров за час оказалось отрицательным?",
    "Какое суммарное количество просмотров набрали все видео, опубликованные в июне 2025 года?"
]

for text in test_queries:
    print(f"\nЗапрос: {text}")
    try:
        query = parse_query(text)
        print("Распознанный запрос:", query)

        if query["query_type"] == "TOTAL_VIDEOS":
            result = total_videos()
        elif query["query_type"] == "CREATOR_VIDEOS_BY_PERIOD":
            result = creator_videos_by_period(
                query["creator_id"],
                query["date_from"],
                query["date_to"],
            )
        elif query["query_type"] == "VIDEOS_VIEWS_GT":
            result = videos_views_gt(
                threshold=query["threshold"],
                creator_id=query["creator_id"],
            )
        elif query["query_type"] == "SUM_DELTA_VIEWS_BY_DAY":
            result = sum_delta_views_by_day(query["date_from"])
        elif query["query_type"] == "VIDEOS_WITH_DELTA_BY_DAY":
            result = videos_with_delta_by_day(query["date_from"])
        elif query["query_type"] == "NEGATIVE_VIEWS_DELTAS_COUNT":
            result = count_negative_views_deltas()
        elif query["query_type"] == "SUM_VIEWS_BY_MONTH":
            result = sum_views_by_month(query["month"], query["year"])
        else:
            result = "Неизвестный query_type"

        print("Результат:", result)

    except Exception as e:
        print("Ошибка:", e)
