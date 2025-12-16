import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
SYSTEM_PROMPT = """

{
  "query_type": "...",
  "creator_id": "uuid или null",
  "date_from": "YYYY-MM-DD или null",
  "date_to": "YYYY-MM-DD или null",
  "threshold": number или null
}
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
