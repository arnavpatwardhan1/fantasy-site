from flask import Flask, render_template, request
from sleeper import build_team_data, build_matchup_data
import json

app = Flask(__name__)

# Replace this with your actual Sleeper league ID
LEAGUE_ID = "1221181311436201984"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/teams")
def teams():
    team_data = build_team_data(LEAGUE_ID)
    return render_template("teams.html", teams=team_data)

@app.route("/week/<int:week>")
def matchups(week):
    matchup_data = build_matchup_data(LEAGUE_ID, week)
    return render_template("matchups.html", matchups=matchup_data, week=week)

@app.route('/compare', methods=['GET', 'POST'])
def compare():
    teams = build_team_data(LEAGUE_ID)

    selected_team1_id = request.form.get('team1')
    selected_team2_id = request.form.get('team2')
    grouping = request.form.get('grouping', 'starters_bench')  # default grouping

    team1 = next((t for t in teams if t['id'] == selected_team1_id), None)
    team2 = next((t for t in teams if t['id'] == selected_team2_id), None)

    def group_players(team):
        if not team:
            return {"QB": [], "RB": [], "WR": [], "TE": [], "Other": []}

        players = team['starters'] + team['bench']

        if grouping == 'by_position':
            groups = {"QB": [], "RB": [], "WR": [], "TE": [], "Other": []}
            for p in players:
                pos = p['position']
                if pos in groups:
                    groups[pos].append(p)
                else:
                    groups["Other"].append(p)
            return groups
        else:
            # starters and bench grouping
            return {
                "Starters": team['starters'],
                "Bench": team['bench']
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