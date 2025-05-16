from openai import OpenAI
import os
from dotenv import load_dotenv
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


load_dotenv()  # Loads from .env


def parse_query_with_gpt(user_input: str) -> dict:
    prompt = f"""
You are a natural language to NBA stats translator. Your job is to take user questions and output structured JSON instructions.

Here are some examples:
---
User: who led the league in assists last season?
Output:
{{
  "action": "get_stat_leader",
  "stat": "assists",
  "season": "2023-2024"
}}
---
User: show me LeBron James' points per game over the last 5 years
Output:
{{
  "action": "get_player_stats",
  "player": "LeBron James",
  "stat": "points_per_game",
  "range": "last 5 years"
}}
---
Now here is the user question:
User: {user_input}
Output:
"""

    response = client.chat.completions.create(model="gpt-4o",
    temperature=0,
    messages=[{"role": "user", "content": prompt}])

    output_text = response.choices[0].message.content

    try:
        json_start = output_text.find("{")
        json_end = output_text.rfind("}") + 1
        json_str = output_text[json_start:json_end]
        return eval(json_str)
    except Exception as e:
        print("⚠️ Error parsing GPT output:", e)
        return {"error": "could not parse"}
