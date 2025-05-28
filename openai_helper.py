from openai import OpenAI
import json
import os
from dotenv import load_dotenv

load_dotenv()  # Loads from .env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


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
User: who led the league in assists this season?
Output:
{{
  "action": "get_stat_leader",
  "stat": "assists",
  "season": "2024-2025"
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
User: compare LeBron James and Kevin Durant in points, assists, and rebounds this season
Output:
{{
  "action": "compare_players",
  "players": ["LeBron James", "Kevin Durant"],
  "stats": ["points", "assists", "rebounds"],
  "season": "2024-2025"
}}
---
---
User: compare Jayson Tatum and Jimmy Butler in points per game and rebounds this season
Output:
{{
  "action": "compare_players",
  "players": ["Jayson Tatum", "Jimmy Butler"],
  "stats": ["points per game", "rebounds"],
  "season": "2024-2025",
  "per_game": true
}}
---
User: Who leads the Warriors in scoring this season?
Output:
{{
  "action": "get_team_leader",
  "team_name": "Warriors",
  "stat_name": "scoring", 
  "season": "2024-2025"
}}
---
User: who has the most free throw attempts in the nba playoffs right now?
Output:
{{
  "action": "get_top_players",
  "stat": "free throw attempts",
  "season": "2024-2025",
  "season_type": "Playoffs",
  "limit": 5
}}
---
User: What's the Lakers' record this season?
Output:
{{
  "action": "get_team_record",
  "team_name": "Lakers",
  "season": "2024-2025"
}}
---
Now here is the user question:
User: {user_input}
Output:
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )

    output_text = response.choices[0].message.content

    try:
        json_start = output_text.find("{")
        json_end = output_text.rfind("}") + 1
        json_str = output_text[json_start:json_end]
        return json.loads(json_str)
    except Exception as e:
        print("⚠️ Error parsing GPT output:", e)
        return {"error": "could not parse"}
