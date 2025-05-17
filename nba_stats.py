from nba_api.stats.endpoints import leaguedashplayerstats, playercareerstats
from nba_api.stats.static import players
import pandas as pd
import re # For parsing range
from datetime import datetime # For determining current year

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
        "steals per game": "STL",
        "blocks per game": "BLK",
        # Adding underscore versions, as produced by GPT
        "points_per_game": "PTS",
        "assists_per_game": "AST",
        "rebounds_per_game": "REB",
        "steals_per_game": "STL",
        "blocks_per_game": "BLK"
        # Removed duplicate entries for "points", "assists", "rebounds" that were at the end
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

def get_player_id(player_name: str):
    player_find = players.find_players_by_full_name(player_name)
    if not player_find:
        return None
    return player_find[0]['id']

def parse_season_range(season_range_str: str) -> list[str]:
    match = re.match(r"last (\d+) (?:years|seasons)", season_range_str.lower())
    if not match:
        # Try to parse a single season or direct range like "2020-21 to 2022-23"
        # For simplicity, we'll assume single season if not "last X years"
        # A more robust solution would handle more complex range strings
        normalized = normalize_season(season_range_str)
        if normalized != season_range_str: # It was a known alias like "last season"
             return [normalized]
        if re.match(r"^\d{4}-\d{2}$", normalized): # Format YYYY-YY
            return [normalized]
        return [] # Or raise an error for unparseable range

    num_years = int(match.group(1))
    current_year = datetime.now().year
    
    # NBA season spans two calendar years, e.g., 2023-24.
    # If current month is before October (start of new season), current NBA season is (current_year-1)-current_year.
    # Otherwise, it's current_year-(current_year+1).
    # For "last X years", we generally mean completed seasons.
    # Let's assume "last season" refers to the most recently *completed* season.
    # If it's August 2024, "last season" is 2023-24. "Last 3 seasons" are 2021-22, 2022-23, 2023-24.

    most_recent_full_season_end_year = current_year if datetime.now().month >= 7 else current_year -1 # Assuming season ends around June
    
    seasons = []
    for i in range(num_years):
        end_year = most_recent_full_season_end_year - i
        start_year = end_year - 1
        seasons.append(f"{start_year}-{str(end_year)[-2:]}")
    return sorted(seasons) # Return in chronological order


def get_player_stats_over_seasons(player_name: str, stat_name: str, season_range: str):
    player_id = get_player_id(player_name)
    if not player_id:
        return f"❌ Player \'{player_name}\' not found."

    stat_column_api = stat_name_to_column(stat_name)
    # The playercareerstats endpoint uses "PerGame" or "Totals", let's assume "PerGame" based on example
    # "points per game" implies PerGame mode.
    
    career_stats_df = playercareerstats.PlayerCareerStats(player_id=player_id, per_mode36="PerGame").get_data_frames()[0]

    if career_stats_df.empty:
        return f"❌ No career stats found for {player_name}."

    if stat_column_api not in career_stats_df.columns:
        # Check common alternative naming for per game stats
        if stat_name.endswith(" per game") and stat_name_to_column(stat_name.replace(" per game", "")) in career_stats_df.columns:
            stat_column_api = stat_name_to_column(stat_name.replace(" per game", ""))
        else:
            return f"❌ Stat \'{stat_name}\' (mapped to \'{stat_column_api}\') not found in player's career stats."

    target_seasons = parse_season_range(season_range)
    if not target_seasons:
        return f"❌ Could not parse season range: \'{season_range}\'. Try 'last X years' or a specific season like '2022-23'."

    # Filter stats for the target seasons
    player_season_stats = career_stats_df[career_stats_df['SEASON_ID'].isin(target_seasons)]

    if player_season_stats.empty:
        return f"❌ No stats found for {player_name} in the specified seasons: {', '.join(target_seasons)}."
        
    # Select and rename columns for display
    # Ensure PLAYER_NAME is included if not already, for context, though the query is for one player.
    # playercareerstats doesn't have PLAYER_NAME, but we have it.
    result_df = player_season_stats[['SEASON_ID', stat_column_api]].copy()
    result_df.rename(columns={'SEASON_ID': 'SEASON', stat_column_api: stat_name.upper()}, inplace=True)
    
    # Add player name column for clarity, though it's for a single player
    result_df.insert(0, 'PLAYER_NAME', player_name)

    return result_df

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
