import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

from parser import parse_query
from queries import (
    total_videos,
    creator_videos_by_period,
    videos_views_gt,
    sum_delta_views_by_day,
    videos_with_delta_by_day,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")


async def start_handler(message: types.Message):
    await message.answer("Бот аналитики по видео запущен. Задайте вопрос.")


async def message_handler(message: types.Message):
    try:
        query = parse_query(message.text)
        print("PARSED:", query)  # можно потом удалить

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
            result = sum_delta_views_by_day(
                query["date_from"],
            )

        elif query["query_type"] == "VIDEOS_WITH_DELTA_BY_DAY":
            result = videos_with_delta_by_day(
                query["date_from"],
            )

        else:
            raise ValueError("Unknown query type")

        await message.answer(str(result))

    except Exception as e:
        print("ERROR:", e)
        await message.answer("Не удалось обработать запрос")


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
