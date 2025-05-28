# Chat NBA 🏀

Welcome to Chat NBA! Ask anything about NBA player and team statistics using natural language.
This command-line application leverages the OpenAI API to understand your questions and the `nba_api` to fetch official NBA stats.

## Features

Chat NBA can understand a variety of questions about NBA statistics, including:

*   **League Leaders**: Find out who leads the league (or top N players) in a specific stat for a given season (e.g., "Who led the league in rebounds last season?", "Top 5 in 3PT% this season?"). Supports regular season and playoffs.
*   **Player Season Stats**: Get a player's specific stat over multiple seasons (e.g., "Show me Steph Curry's points per game over the last 3 seasons").
*   **Player Comparison**: Compare multiple players across several stats for a season (e.g., "Compare LeBron James and Kevin Durant in points, assists, and rebounds this season"). Supports per-game stats.
*   **Team Leaders**: Find out which player leads a specific team in a given stat for a season (e.g., "Who leads the Warriors in scoring this season?").
*   **Team Records**: Get a team's win-loss record and conference standing for a season (e.g., "What's the Lakers' record this season?").
*   **Stat Explanations**: Get a clear explanation of what a specific NBA statistic means (e.g., "What does PER mean?").
*   **League Averages**: Calculate the league average for a specific stat in a given season (e.g., "What's the league average for 3PT% this season?"). Supports regular season and playoffs.
*   **Player Game Logs**: Show a player's performance in their most recent games (e.g., "Show me Devin Booker's last 5 games"). Supports regular season and playoffs.

## Setup Instructions

1.  **Clone the Repository (Optional)**:
    If you've received this as a set of files, you can skip this. If it's a Git repository:
    ```bash
    git clone <repository_url>
    cd chat-nba
    ```

2.  **Create and Activate a Virtual Environment**:
    It's highly recommended to use a virtual environment.
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
    (On Windows, use `.venv\Scripts\activate`)

3.  **Install Dependencies**:
    Ensure your virtual environment is active, then run:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up OpenAI API Key**:
    You'll need an OpenAI API key for the natural language processing.
    *   Create a file named `.env` in the root directory of the project.
    *   Add your API key to this file in the following format:
        ```env
        OPENAI_API_KEY='your_openai_api_key_here'
        ```
    Replace `'your_openai_api_key_here'` with your actual key.

## How to Run

Once the setup is complete and your virtual environment is active:

1.  Navigate to the project's root directory in your terminal.
2.  Run the main application script:
    ```bash
    python main.py
    ```
3.  The Chat NBA banner will appear, and you can start asking questions at the `> ` prompt.
4.  Type `exit` or `quit` to leave the application.

## Available Commands & Example Queries

Here are some examples of what you can ask Chat NBA. The application is flexible with phrasing, so feel free to experiment!

*   **Get Stat Leader / Top Players**:
    *   `Who led the league in assists last season?`
    *   `Top 10 players in 3PT% this season`
    *   `Who has the most steals in the playoffs this year?` (Playoff specific)
    *   `Top 3 in rebounds regular season 2022-23`

*   **Get Player Stats Over Seasons**:
    *   `Show me Steph Curry's points per game over the last 3 seasons`
    *   `LeBron James assists per game last 2 years`

*   **Compare Players**:
    *   `Compare LeBron James and Kevin Durant in points, assists, and rebounds this season`
    *   `Compare Jayson Tatum and Jimmy Butler in points per game and rebounds this season per game`

*   **Get Team Leaders**:
    *   `Who leads the Warriors in scoring this season?`
    *   `Who is the 76ers leader in blocks last season?`

*   **Get Team Records**:
    *   `What's the Lakers' record this season?`
    *   `Celtics record 2022-23`

*   **Explain Stat**:
    *   `What does PER mean?`
    *   `Explain True Shooting Percentage`
    *   `Tell me about usage rate`

*   **Get League Average**:
    *   `What's the league average for 3PT% this season?`
    *   `League average for points per game last season`
    *   `Average steals in the playoffs this year?`

*   **Get Player Game Log**:
    *   `Show me Devin Booker's last 5 games`
    *   `LeBron James last 3 games this season`
    *   `Stephen Curry game log last 2 playoff games this season`

## Example Interaction

```
> Welcome to Chat NBA! Ask me anything about NBA stats.
> (Type 'exit' to quit)

> Who led the league in points per game last season?

Thinking...

Parsed intent:
{'action': 'get_stat_leader', 'stat': 'points per game', 'season': '2023-2024'}

+---------------+-----------------+
| PLAYER_NAME   |   POINTS PER GAME |
+===============+=================+
| Joel Embiid   |            33.1 |
+---------------+-----------------+

> Compare Joel Embiid and Nikola Jokic in points, rebounds, and assists last season

Thinking...

Parsed intent:
{'action': 'compare_players', 'players': ['Joel Embiid', 'Nikola Jokic'], 'stats': ['points', 'rebounds', 'assists'], 'season': '2023-2024'}

+----------+---------------+--------------+
| STAT     |   JOEL EMBIID | NIKOLA JOKIC |
+==========+===============+==============+
| PTS      |          2183 |         1904 |
| REB      |           670 |          942 |
| AST      |           274 |          780 |
+----------+---------------+--------------+

> exit
Goodbye!
```

## Troubleshooting & Notes

*   **API Keys**: Ensure your `OPENAI_API_KEY` in the `.env` file is correct and has not exceeded its quota.
*   **Data Freshness**: Statistics are fetched live from the `nba_api`. The most current data depends on when the API updates.
*   **Stat Availability**: Some advanced or very specific stats might not be directly available or mapped. If a stat isn't found, the application will let you know.
*   **Team Names**: The application tries to match common team names (e.g., "Lakers", "Warriors", "Sixers"). For less common references, using the full team name (e.g., "Golden State Warriors") might be more reliable.

## Future Enhancements (Backlog)

*   **Game Scores**: Functionality to retrieve scores of specific past games (e.g., "What was the score of the Celtics vs Bucks game on April 5th?") is currently in the backlog due to API complexities.
*   **Contextual Follow-up Queries**: Improving the ability to have more continuous conversations, such as adding a player to a previously generated comparison table.

--- 

Happy Chatting About NBA! 🏀 