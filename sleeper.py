import requests

BASE_URL = "https://api.sleeper.app/v1"


def get_league_users(league_id):
    url = f"{BASE_URL}/league/{league_id}/users"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def get_league_rosters(league_id):
    url = f"{BASE_URL}/league/{league_id}/rosters"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def get_matchups(league_id, week):
    url = f"{BASE_URL}/league/{league_id}/matchups/{week}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def get_league_info(league_id):
    url = f"{BASE_URL}/league/{league_id}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def get_user_display_name_map(league_id):
    users = get_league_users(league_id)
    return {user['user_id']: user['display_name'] for user in users}


def get_player_name_map():
    url = f"{BASE_URL}/players/nfl"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    player_map = {}
    for pid, pinfo in data.items():
        player_map[pid] = {
            "name": pinfo.get("full_name", "Unknown"),
            "position": pinfo.get("position", "")
        }
    return player_map



def build_team_data(league_id):
    user_map = get_user_display_name_map(league_id)
    rosters = get_league_rosters(league_id)
    player_map = get_player_name_map()

    teams = []
    for r in rosters:
        user_id = r.get("owner_id")
        all_players = r.get("players", [])
        starters = r.get("starters", [])
        bench = [p for p in all_players if p not in starters]

        starters_named = [
            {
                "name": player_map.get(pid, {}).get("name", pid),
                "position": player_map.get(pid, {}).get("position", ""),
                "rank": player_map.get(pid, {}).get("rank", "N/A")
            } for pid in starters
        ]
        bench_named = [
            {
                "name": player_map.get(pid, {}).get("name", pid),
                "position": player_map.get(pid, {}).get("position", ""),
                "rank": player_map.get(pid, {}).get("rank", "N/A")
            } for pid in bench
        ]

        team = {
            "id": str(r.get("roster_id")),
            "owner": user_map.get(user_id, "Unknown"),
            "record": f"{r.get('settings', {}).get('wins', 0)}-{r.get('settings', {}).get('losses', 0)}",
            "starters": starters_named,
            "bench": bench_named
        }
        teams.append(team)
    return teams


def build_matchup_data(league_id, week):
    rosters = get_league_rosters(league_id)
    user_map = get_user_display_name_map(league_id)
    matchups = get_matchups(league_id, week)

    roster_id_to_user = {r['roster_id']: user_map.get(r['owner_id'], 'Unknown') for r in rosters}

    games = []
    matchup_dict = {}
    for m in matchups:
        matchup_id = m['matchup_id']
        roster_id = m['roster_id']
        team_data = {
            'roster_id': roster_id,
            'owner': roster_id_to_user.get(roster_id, 'Unknown'),
            'points': m.get('points', 0)
        }
        if matchup_id not in matchup_dict:
            matchup_dict[matchup_id] = [team_data]
        else:
            matchup_dict[matchup_id].append(team_data)

    for teams in matchup_dict.values():
        if len(teams) == 2:
            games.append({"home": teams[0], "away": teams[1]})

    return games
