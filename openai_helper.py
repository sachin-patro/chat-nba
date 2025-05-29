from openai import OpenAI
import json
import os
from dotenv import load_dotenv

load_dotenv()  # Loads from .env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_stat_explanation_with_gpt(stat_name: str) -> str:
    prompt = f"""
    You are an expert NBA analyst. Explain the basketball statistic "{stat_name}" in a clear and concise way. 
    Describe what it measures, how it's generally calculated (if common knowledge or simple), and what a high or low value might indicate. 
    Keep the explanation suitable for a knowledgeable basketball fan who may not know this specific term.
    Do not return JSON, just the plain text explanation.
    Example for "FG%":
    Field Goal Percentage (FG%) measures a player's shooting efficiency from the field. It's calculated by dividing the number of field goals made by the total number of field goals attempted. A higher FG% indicates better shooting accuracy. For example, a 50% FG% means the player makes half of their shots.

    Now, explain "{stat_name}":
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o", # Or your preferred model for explanations
            temperature=0.2, # Slightly more creative for explanations
            messages=[{"role": "user", "content": prompt}]
        )
        explanation = response.choices[0].message.content
        return explanation.strip()
    except Exception as e:
        print(f"⚠️ Error getting explanation from GPT for {stat_name}:", e)
        return f"Sorry, I couldn't fetch an explanation for {stat_name} at the moment."


def answer_historical_nba_fact_with_gpt(user_query_details: dict) -> str:
    """
    Answers a historical NBA factual question using GPT.
    """
    original_question = user_query_details.get("original_question", "that specific NBA historical fact")

    prompt = f"""\
You are an NBA historian. Provide a concise answer to the following NBA historical question:
"{original_question}"

If the question is about a specific number (e.g., "how many times..."), provide the number and a brief context if relevant.
For example, if the question is "how many teams have come back from 3-1 down in the playoffs?", a good answer would be:
"As of my last update, 13 teams have come back from a 3-1 deficit to win an NBA playoff series. The most recent was the Denver Nuggets in 2020, who did it twice in the same postseason."

Do not return JSON, just the plain text answer.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o", 
            temperature=0.1, 
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content
        return answer.strip()
    except Exception as e:
        print(f"⚠️ Error getting historical NBA fact from GPT for query '{original_question}':", e)
        return f"Sorry, I couldn't answer the historical question '{original_question}' at the moment."


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
User: What does PER mean?
Output:
{{
  "action": "explain_stat",
  "stat_name": "PER"
}}
---
User: What's the league average for 3PT% this season?
Output:
{{
  "action": "get_league_average",
  "stat_name": "3PT%",
  "season": "2024-2025"
}}
---
User: Show me Devin Booker's last 5 games
Output:
{{
  "action": "get_player_game_log",
  "player_name": "Devin Booker",
  "season": "2024-2025",
  "limit": 5
}}
---
User: how many teams have come back from 3-1 down in the playoffs?
Output:
{{
  "action": "get_historical_nba_fact",
  "original_question": "how many teams have come back from 3-1 down in the playoffs?"
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
