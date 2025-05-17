from utils import print_banner
from openai_helper import parse_query_with_gpt
from nba_stats import get_top_players_by_stat, compare_players
import pandas as pd
from tabulate import tabulate

def main():
    print_banner()
    print("Welcome to Chat NBA! Ask me anything about NBA stats.")
    print("(Type 'exit' to quit)\n")

    while True:
        user_input = input("> ")

        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        print("\nThinking...\n")
        result = parse_query_with_gpt(user_input)
        print("Parsed intent:")
        print(result)
        print()

        if result.get("action") == "get_top_players":
            table = get_top_players_by_stat(
                stat_name=result.get("stat", ""),
                season=result.get("season", ""),
                limit=result.get("limit", 5)
            )
            if isinstance(table, pd.DataFrame):
                print(tabulate(table, headers='keys', tablefmt='grid', showindex=False))
            else:
                print(table)
            print()

        elif result.get("action") == "compare_players":
            table = compare_players(
                player_names=result.get("players", []),
                stat_names=result.get("stats", []),
                season=result.get("season", ""),
                per_game=result.get("per_game", False)
            )
            if isinstance(table, pd.DataFrame):
                print(tabulate(table, headers='keys', tablefmt='grid', showindex=False))
            else:
                print(table)
            print()

if __name__ == "__main__":
    main()
