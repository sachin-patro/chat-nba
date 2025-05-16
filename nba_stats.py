from nba_api.stats.endpoints import leaguedashplayerstats
import pandas as pd

def get_top_players_by_stat(stat_name: str, season: str, limit: int = 5):
    # nba_api expects season format like '2023-24'
    season = season.replace("2023-2024", "2023-24")  # basic fix; you can expand this later

    # Fetch data from NBA stats API
    stats = leaguedashplayerstats.LeagueDashPlayerStats(season=season).get_data_frames()[0]

    # Normalize stat name for lookup (expand later with aliases)
    stat_column = stat_name_to_column(stat_name)

    if stat_column not in stats.columns:
        return f"❌ Stat '{stat_name}' not found in data."

    # Sort and filter top players
    top_players = stats.sort_values(by=stat_column, ascending=False).head(limit)

    # Select just name + stat column
    return top_players[['PLAYER_NAME', stat_column]]

def stat_name_to_column(stat_name: str) -> str:
    # Expand this as you go; basic alias mapping
    mapping = {
        "points": "PTS",
        "assists": "AST",
        "rebounds": "REB",
        "steals": "STL",
        "blocks": "BLK",
        "3-point percentage": "FG3_PCT",
        "field goal %": "FG_PCT",
        "free throw %": "FT_PCT"
    }
    return mapping.get(stat_name.lower(), stat_name)
