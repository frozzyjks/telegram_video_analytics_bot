import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

from db import get_connection
from parser import parse_query
from queries import (
    total_videos,
    creator_videos_by_period,
    videos_views_gt,
    sum_delta_views_by_day,
    videos_with_delta_by_day,
    count_negative_views_deltas,
    sum_views_by_month,
    sum_delta_views_by_interval,
    count_creators_with_videos_views_gt,
    count_creator_published_days,
    creator_active_days_in_month
)

BOT_TOKEN = os.getenv("BOT_TOKEN")


async def start_handler(message: types.Message):
    await message.answer("Бот аналитики по видео запущен. Задайте вопрос.")


async def message_handler(message: types.Message):
    text = message.text.strip()
    print("Incoming message:", repr(text))
    try:
        query = parse_query(text)
        print("Parsed query:", query)
        conn = get_connection()

        if query["query_type"] == "TOTAL_VIDEOS":
            result = total_videos(conn)

        elif query["query_type"] == "CREATORS_WITH_VIDEOS_VIEWS_GT":

            result = count_creators_with_videos_views_gt(query["threshold"])

        elif query["query_type"] == "CREATOR_VIDEOS_BY_PERIOD":
            result = creator_videos_by_period(
                conn,
                query["creator_id"],
                query["date_from"],
                query["date_to"],
            )

        elif query["query_type"] == "VIDEOS_VIEWS_GT":
            result = videos_views_gt(
                conn,
                threshold=query["threshold"],
                creator_id=query["creator_id"],
            )

        elif query["query_type"] == "SUM_DELTA_VIEWS_BY_DAY":
            result = sum_delta_views_by_day(conn, query["date_from"])

        elif query["query_type"] == "VIDEOS_WITH_DELTA_BY_DAY":
            result = videos_with_delta_by_day(conn, query["date_from"])

        elif query["query_type"] == "NEGATIVE_VIEWS_DELTAS_COUNT":
            result = count_negative_views_deltas(conn)

        elif query["query_type"] == "SUM_VIEWS_BY_MONTH":
            result = sum_views_by_month(conn, query["month"], query["year"])

        elif query["query_type"] == "SUM_DELTA_VIEWS_BY_INTERVAL":
            result = sum_delta_views_by_interval(
                conn,
                query["creator_id"],
                query["date"],
                query["start_time"],
                query["end_time"]
            )
        elif query["query_type"] == "CREATOR_PUBLISHED_DAYS_COUNT":
            result = count_creator_published_days(
                query["creator_id"],
                query["month"],
                query["year"]
            )

        elif query["query_type"] == "CREATOR_ACTIVE_DAYS_IN_MONTH":
            result = creator_active_days_in_month(
                query["creator_id"],
                query["month"],
                query["year"]
            )

        else:
            raise ValueError("Unknown query type")

        await message.answer(str(result))

    except Exception as e:
        print("ERROR:", e)
        await message.answer("Не удалось обработать запрос")

    finally:
        try:
            conn.close()
        except Exception:
            pass


async def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not set")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.message.register(start_handler, CommandStart())
    dp.message.register(message_handler)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
