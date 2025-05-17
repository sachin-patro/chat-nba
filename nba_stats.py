from nba_api.stats.endpoints import leaguedashplayerstats
import pandas as pd

def get_top_players_by_stat(stat_name: str, season: str, limit: int = 5):
    season = normalize_season(season)

    stats = leaguedashplayerstats.LeagueDashPlayerStats(season=season).get_data_frames()[0]
    stat_column = stat_name_to_column(stat_name)

    if stat_column not in stats.columns:
        return f"❌ Stat '{stat_name}' not found in data."

    # Add filters to exclude players with too few attempts
    if stat_column == "FG3_PCT":
        stats = stats[stats["FG3A"] > 100]  # e.g. min 100 3PA
    elif stat_column == "FT_PCT":
        stats = stats[stats["FTA"] > 100]   # e.g. min 100 FTA
    elif stat_column == "FG_PCT":
        stats = stats[stats["FGA"] > 300]   # min 300 FG attempts

    # Sort and limit
    top_players = stats.sort_values(by=stat_column, ascending=False).head(limit)
    return top_players[['PLAYER_NAME', stat_column]]


def stat_name_to_column(stat_name: str) -> str:
    mapping = {
        "points": "PTS",
        "assists": "AST",
        "rebounds": "REB",
        "steals": "STL",
        "blocks": "BLK",
        "3-point percentage": "FG3_PCT",
        "3pt%": "FG3_PCT",
        "3pt": "FG3_PCT",
        "fg3%": "FG3_PCT",
        "fg%": "FG_PCT",
        "field goal %": "FG_PCT",
        "free throw %": "FT_PCT",
        "ft%": "FT_PCT",
        "points per game": "PTS",
        "assists per game": "AST",
        "rebounds per game": "REB",
        "points": "PTS",
        "assists": "AST",
        "rebounds": "REB"
        
    }
    return mapping.get(stat_name.lower(), stat_name)


def normalize_season(season: str) -> str:
    mapping = {
        "2023-2024": "2023-24",
        "2024-2025": "2024-25",
        "2022-2023": "2022-23",
        "2021-2022": "2021-22",
        "last season": "2023-24",
        "this season": "2024-25"
    }
    return mapping.get(season.lower(), season)

def compare_players(player_names: list, stat_names: list, season: str, per_game: bool = False):
    season = normalize_season(season)
    stat_columns = [stat_name_to_column(stat) for stat in stat_names]

    # Fetch all player stats from the league
    per_mode = "PerGame" if per_game else "Totals"
    all_stats = leaguedashplayerstats.LeagueDashPlayerStats(
        season=season,
        per_mode_detailed=per_mode
    ).get_data_frames()[0]


    # Filter for the requested players
    filtered = all_stats[all_stats["PLAYER_NAME"].isin(player_names)]

    if filtered.empty:
        return f"❌ Could not find one or more players in the current season."

    # Build a comparison table
    data = []
    for stat in stat_columns:
        if stat not in filtered.columns:
            return f"❌ Stat '{stat}' not available."
        row = [stat]
        for player in player_names:
            player_row = filtered[filtered["PLAYER_NAME"] == player]
            if not player_row.empty:
                row.append(round(player_row[stat].values[0], 2))
            else:
                row.append("N/A")
        data.append(row)

    columns = ["STAT"] + player_names
    return pd.DataFrame(data, columns=columns)
