from nba_api.stats.endpoints import leaguedashplayerstats, playercareerstats, leaguestandingsv3
from nba_api.stats.static import players, teams
import pandas as pd
import re # For parsing range
from datetime import datetime # For determining current year

def get_top_players_by_stat(stat_name: str, season: str, limit: int = 5, season_type: str = "Regular Season"):
    season = normalize_season(season)

    stats = leaguedashplayerstats.LeagueDashPlayerStats(
        season=season,
        season_type_all_star=season_type
    ).get_data_frames()[0]
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
        "free throw attempts": "FTA",
        "free throws made": "FTM",
        "free throws": "FTM",
        "fta": "FTA",
        "ftm": "FTM",
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

def get_team_id(team_name_query: str) -> int | None:
    # Attempt to find by full name (returns a list)
    found_team_list = teams.find_teams_by_full_name(team_name_query)
    if found_team_list:
        return found_team_list[0]['id']

    # Attempt to find by nickname (returns a list)
    found_team_list = teams.find_teams_by_nickname(team_name_query)
    if found_team_list:
        return found_team_list[0]['id']

    # Attempt to find by abbreviation (returns a dict or None)
    team_by_abbr = teams.find_team_by_abbreviation(team_name_query) # Corrected method name
    if team_by_abbr:
        return team_by_abbr['id'] # Directly access id from dict

    # Attempt to find by city (returns a list)
    found_team_list = teams.find_teams_by_city(team_name_query)
    if found_team_list:
        return found_team_list[0]['id']
    
    # Simple custom mapping for common names GPT might produce
    custom_mapping = { 
        "warriors": "Golden State Warriors",
        "lakers": "Los Angeles Lakers",
        "celtics": "Boston Celtics",
        "bucks": "Milwaukee Bucks",
        "sixers": "Philadelphia 76ers", 
        # Add more as needed
    }
    normalized_query = team_name_query.lower()
    if normalized_query in custom_mapping:
        # If custom mapping matches, search by the mapped full name
        mapped_full_name = custom_mapping[normalized_query]
        found_team_list_custom = teams.find_teams_by_full_name(mapped_full_name)
        if found_team_list_custom:
            return found_team_list_custom[0]['id']

    return None

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

def get_team_leader(team_name: str, stat_name: str, season: str):
    normalized_season = normalize_season(season)
    team_id = get_team_id(team_name)

    if not team_id:
        return f"❌ Team '{team_name}' not found."

    # GPT might send "scoring" for "points"
    if stat_name.lower() == "scoring":
        stat_name = "points"
    
    stat_column = stat_name_to_column(stat_name)
    
    # Determine if per_game is implied by the stat name
    per_game_implied = "per game" in stat_name.lower() or "_per_game" in stat_name.lower()
    per_mode_request = "PerGame" if per_game_implied else "Totals"

    try:
        team_player_stats_df = leaguedashplayerstats.LeagueDashPlayerStats(
            season=normalized_season,
            team_id_nullable=team_id,
            per_mode_detailed=per_mode_request 
        ).get_data_frames()[0]
    except Exception as e:
        return f"❌ Error fetching team stats: {e}"

    if team_player_stats_df.empty:
        return f"❌ No player stats found for {team_name} in season {normalized_season} (Mode: {per_mode_request})."

    if stat_column not in team_player_stats_df.columns:
        # If original stat_name was 'scoring' and mapped to 'PTS', and 'PTS' is not found,
        # it's a genuine missing column.
        return f"❌ Stat '{stat_name}' (mapped to '{stat_column}') not found for {team_name} in season {normalized_season} (Mode: {per_mode_request}). Available columns: {team_player_stats_df.columns.tolist()}"

    # Apply similar FG_PCT, FT_PCT, FG3_PCT filters as in get_top_players_by_stat if applicable
    if stat_column == "FG3_PCT":
        team_player_stats_df = team_player_stats_df[team_player_stats_df["FG3A"] > 10] # Lower threshold for single team leader
    elif stat_column == "FT_PCT":
        team_player_stats_df = team_player_stats_df[team_player_stats_df["FTA"] > 10]
    elif stat_column == "FG_PCT":
        team_player_stats_df = team_player_stats_df[team_player_stats_df["FGA"] > 20]
        
    if team_player_stats_df.empty:
         return f"❌ No players found for {team_name} in season {normalized_season} after applying minimum attempt filters for {stat_column}."

    # Sort to find the leader
    # For percentage stats, ensure the player has a reasonable number of attempts (already partly handled)
    leader_df = team_player_stats_df.sort_values(by=stat_column, ascending=False).head(1)

    if leader_df.empty:
        return f"❌ Could not determine a leader for {stat_name} for {team_name} in {normalized_season}."

    leader_name = leader_df.iloc[0]['PLAYER_NAME']
    leader_stat_value = leader_df.iloc[0][stat_column]
    
    # Create a small DataFrame for consistent output
    result_data = {'PLAYER_NAME': [leader_name], stat_column: [leader_stat_value]}
    result_df = pd.DataFrame(result_data)
    result_df.rename(columns={stat_column: stat_name.upper()}, inplace=True)
    return result_df

def get_team_record(team_name: str, season: str):
    normalized_season = normalize_season(season)
    team_id = get_team_id(team_name)

    if not team_id:
        return f"❌ Team '{team_name}' not found."

    # Season format for LeagueStandingsV3 is YYYY-YY, e.g., 2023-24
    # normalize_season should already provide this format.

    try:
        standings = leaguestandingsv3.LeagueStandingsV3(season=normalized_season)
        # The first DataFrame in the result set usually contains the standings data.
        standings_df = standings.get_data_frames()[0] 
    except Exception as e:
        return f"❌ Error fetching standings data: {e}"

    if standings_df.empty:
        return f"❌ No standings data found for season {normalized_season}."

    team_standings = standings_df[standings_df['TeamID'] == team_id]

    if team_standings.empty:
        return f"❌ Could not find standings for {team_name} (ID: {team_id}) in season {normalized_season}."

    # Extract relevant information
    record = team_standings.iloc[0].get('Record', 'N/A')
    conf_rank = team_standings.iloc[0].get('ConferenceRecord', 'N/A').split('-')[0] # often 'W-L in Conf', take W
    # Or more directly, some versions have 'PlayoffRank' or 'ConferenceRank'
    # Let's check for a more direct conference rank column if available.
    # Common column names: 'ConferenceRank', 'PlayoffRank', 'ClinchIndicator' (might show rank)
    # For simplicity, we will stick to common ones or construct from Record.
    
    # We need TEAM, W, L, CONF_RANK, (maybe PCT)
    wins = team_standings.iloc[0].get('WINS', record.split('-')[0] if record != 'N/A' else 'N/A')
    losses = team_standings.iloc[0].get('LOSSES', record.split('-')[1] if record != 'N/A' and '-' in record else 'N/A')
    win_pct = team_standings.iloc[0].get('WinPCT', 'N/A')
    # Use 'ConferenceRank' if available, otherwise parse from 'ConferenceRecord'
    conference_rank = team_standings.iloc[0].get('ConferenceRank', 
                                                 team_standings.iloc[0].get('PlayoffRank', 'N/A'))
    team_city = team_standings.iloc[0].get('TeamCity', team_name.split()[:-1] if len(team_name.split()) > 1 else team_name) # Guess city
    actual_team_name = team_standings.iloc[0].get('TeamName', team_name.split()[-1]) # Guess name part
    display_name = f"{team_city} {actual_team_name}"

    result_data = [{
        'TEAM': display_name,
        'W': wins,
        'L': losses,
        'PCT': f"{win_pct:.3f}" if isinstance(win_pct, float) else win_pct,
        'CONF_RANK': conference_rank
    }]
    
    return pd.DataFrame(result_data)

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
