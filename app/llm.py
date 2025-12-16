import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
SYSTEM_PROMPT = """
Ты — парсер пользовательских запросов к аналитической системе.
Твоя задача — преобразовать текстовый запрос на русском языке
в СТРОГИЙ JSON следующего формата:

{
  "query_type": "...",
  "creator_id": "uuid или null",
  "date_from": "YYYY-MM-DD или null",
  "date_to": "YYYY-MM-DD или null",
  "threshold": number или null
}

Поддерживаемые типы query_type:
- TOTAL_VIDEOS — сколько всего видео
- CREATOR_VIDEOS_BY_PERIOD — сколько видео у креатора за период
- VIDEOS_VIEWS_GT — сколько видео с просмотрами больше порога
- SUM_DELTA_VIEWS_BY_DAY — суммарный прирост просмотров за день
- VIDEOS_WITH_DELTA_BY_DAY — сколько видео получили новые просмотры за день

Правила:
- возвращай ТОЛЬКО JSON
- не добавляй комментарии
- даты возвращай в формате YYYY-MM-DD
- если параметр не нужен — ставь null
"""

def parse_query(text: str) -> dict:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
    )

    content = response.choices[0].message.content
    return json.loads(content)
