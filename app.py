from flask import Flask, render_template, request, redirect, url_for
from sleeper import build_team_data, build_matchup_data
import json
import pandas as pd

app = Flask(__name__)

# Replace this with your actual Sleeper league ID
LEAGUE_ID = "1221181311436201984"
ktc_df = pd.read_csv('ktc_data.csv')

ktc_lookup = {
    row['full_name']: {
        'adp': row['avg_adp'],
        'ktc_value': row['KeepTradeCut']
    }
    for _, row in ktc_df.iterrows()
}




@app.route("/")
def home():
    return render_template("index.html")

@app.route("/teams")
def teams():
    team_data = build_team_data(LEAGUE_ID)

    # Add KTC data to each player
    for team in team_data:
        for player in team['starters']:  # Adjust if your key is different
            name = player.get('full_name') or player.get('name')  # Use fallback
            ktc_data = ktc_lookup.get(name)
            if ktc_data:
                player['adp'] = ktc_data['adp']
                player['ktc_value'] = ktc_data['ktc_value']
            else:
                player['adp'] = 'N/A'
                player['ktc_value'] = 'N/A'
        for player in team['bench']:  # Adjust if your key is different
            name = player.get('full_name') or player.get('name')  # Use fallback
            ktc_data = ktc_lookup.get(name)
            if ktc_data:
                player['adp'] = ktc_data['adp']
                player['ktc_value'] = ktc_data['ktc_value']
            else:
                player['adp'] = 'N/A'
                player['ktc_value'] = 'N/A'

    return render_template("teams.html", teams=team_data)

@app.route("/matchups/<int:week>")
def matchups(week):
    matchup_data = build_matchup_data(LEAGUE_ID, week)
    return render_template("matchups.html", matchups=matchup_data, week=week)

@app.route('/compare', methods=['GET', 'POST'])
def compare():
    teams = build_team_data(LEAGUE_ID)

    # Accept team IDs from GET (for links) or POST (form submit)
    selected_team1_id = request.args.get('team1') or request.form.get('team1')
    selected_team2_id = request.args.get('team2') or request.form.get('team2')
    grouping = request.args.get('grouping') or request.form.get('grouping', 'starters_bench')

    # Find teams and add KTC data
    team1 = None
    team2 = None
    
    if selected_team1_id:
        team1 = next((t for t in teams if t['id'] == selected_team1_id), None)
        if team1:
            for player in team1.get('starters', []):
                name = player.get('full_name') or player.get('name')
                ktc_data = ktc_lookup.get(name)
                player.update({
                    'adp': ktc_data['adp'] if ktc_data else 'N/A',
                    'ktc_value': ktc_data['ktc_value'] if ktc_data else 'N/A'
                })
            for player in team1.get('bench', []):
                name = player.get('full_name') or player.get('name')
                ktc_data = ktc_lookup.get(name)
                player.update({
                    'adp': ktc_data['adp'] if ktc_data else 'N/A',
                    'ktc_value': ktc_data['ktc_value'] if ktc_data else 'N/A'
                })

    if selected_team2_id:
        team2 = next((t for t in teams if t['id'] == selected_team2_id), None)
        if team2:
            for player in team2.get('starters', []):
                name = player.get('full_name') or player.get('name')
                ktc_data = ktc_lookup.get(name)
                player.update({
                    'adp': ktc_data['adp'] if ktc_data else 'N/A',
                    'ktc_value': ktc_data['ktc_value'] if ktc_data else 'N/A'
                })
            for player in team2.get('bench', []):
                name = player.get('full_name') or player.get('name')
                ktc_data = ktc_lookup.get(name)
                player.update({
                    'adp': ktc_data['adp'] if ktc_data else 'N/A',
                    'ktc_value': ktc_data['ktc_value'] if ktc_data else 'N/A'
                })

    # Grouping logic
    def group_players(team):
        if not team:
            return {"QB": [], "RB": [], "WR": [], "TE": [], "Other": []}

        players = team.get('starters', []) + team.get('bench', [])

        if grouping == 'by_position':
            groups = {"QB": [], "RB": [], "WR": [], "TE": [], "Other": []}
            for p in players:
                pos = p.get('position', '').upper()
                if pos in groups:
                    groups[pos].append(p)
                else:
                    groups["Other"].append(p)
            return groups
        else:
            return {
                "Starters": team.get('starters', []),
                "Bench": team.get('bench', [])
            }

    team1_grouped = group_players(team1)
    team2_grouped = group_players(team2)

    return render_template(
        'compare.html',
        teams=teams,
        selected_team1_id=selected_team1_id,
        selected_team2_id=selected_team2_id,
        grouping=grouping,
        team1_grouped=team1_grouped,
        team2_grouped=team2_grouped
    )
    
    


if __name__ == "__main__":
    app.run(debug=True)