from bs4 import BeautifulSoup
from sim_utils.classes import *
import requests
import pandas as pd

# GLOBAL VARIABLES
abbreviations = {
    'ARI': "Arizona D'Backs",
    'ATL': 'Atlanta Braves',
    'BAL': 'Baltimore Orioles',
    'BOS': 'Boston Red Sox',
    'CHC': 'Chicago Cubs',
    'CHW': 'Chicago White Sox',
    'CIN': 'Cincinnati Reds',
    'CLE': 'Cleveland Indians',
    'COL': 'Colorado Rockies',
    'DET': 'Detroit Tigers',
    'HOU': 'Houston Astros',
    'KCR': 'Kansas City Royals',
    'LAA': 'Los Angeles Angels',
    'LAD': 'Los Angeles Dodgers',
    'MIA': 'Miami Marlins',
    'MIL': 'Milwaukee Brewers',
    'MIN': 'Minnesota Twins',
    'NYM': 'New York Mets',
    'NYY': 'New York Yankees',
    'OAK': 'Oakland Athletics',
    'PHI': 'Philadelphia Phillies',
    'PIT': 'Pittsburgh Pirates',
    'SDP': 'San Diego Padres',
    'SEA': 'Seattle Mariners',
    'SFG': 'San Francisco Giants',
    'STL': 'St. Louis Cardinals',
    'TBR': 'Tampa Bay Rays',
    'TEX': 'Texas Rangers',
    'TOR': 'Toronto Blue Jays',
    'WSN': 'Washington Nationals'
}


def get_schedule(year):
    schedule = []

    url = 'https://www.baseball-reference.com/leagues/MLB/' + str(year) + \
          '-schedule.shtml'
    schedule_page = requests.get(url)

    soup = BeautifulSoup(schedule_page.text, 'html.parser')
    games = soup.find_all(class_='game')

    for game in games:
        if game.find('span'):
            continue
        teams = game.find_all('a')
        away_team = teams[0].text
        home_team = teams[1].text

        schedule.append((away_team, home_team))

    return year, schedule


def get_player_batting_df(year):
    df = pd.read_csv("C:/Users/Wideet/Documents/MLB_Data/batting_files/" +
                     str(year) + "_batting.csv")
    # Let's assume we got everything....

    # Preprocess to more easily aggregate to team rosters
    df['Team Name'] = df['Tm'] \
        .apply(lambda x: abbreviations[x] if x in abbreviations else None)
    df['Name'] = df['Name'] \
        .apply(lambda x: x.split('\\')[0].replace('*', '').replace('#', ''))

    # only want 9 players who had the most plate appearances for that team
    roster_indices = list(df.groupby('Tm')['PA'].nlargest(9)
                          .reset_index()['level_1'].values)
    roster_df = df.iloc[roster_indices]
    roster_df = roster_df[roster_df['Tm'].isin(abbreviations)]

    return roster_df


def create_player_from_row(player_row, year):
    player_name = player_row['Name']
    player_PA = player_row['PA']
    player_walks = player_row['BB'] + player_row['HBP'] + player_row['IBB']
    player_hits = player_row['H']
    player_2B = player_row['2B']
    player_3B = player_row['3B']
    player_HR = player_row['HR']
    player_1B = player_hits - player_2B - player_3B - player_HR
    assert player_1B >= 0, "1B Calculation Error"

    return Player(
        name=player_name,
        seasons=[year],
        true_BA=player_hits / player_PA,
        perc_singles=player_1B / player_hits,
        perc_doubles=player_2B / player_hits,
        perc_triples=player_3B / player_hits,
        perc_HR=player_HR / player_hits,
        perc_walk=player_walks / player_PA
    )


def update_player(curr_player, update_player):
    """
    Update an existing Player object with the stats from a new player object

    Parameters
    ----------
    curr_player: Player
        current Player object
    update_player: Player
        Player object with stats to update

    Returns
    -------
    Player
        new Player object with updated stats

    """
    if not curr_player:
        return update_player
    if not update_player:
        return curr_player

    assert (curr_player.name == update_player.name, "player names do not match")

    num_seasons = max(
        len(set(curr_player.seasons + update_player.seasons)), 1)
    true_BA = (curr_player.true_BA*len(curr_player.seasons) +
               update_player.true_BA*len(update_player.seasons)) / num_seasons
    perc_singles = (curr_player.perc_singles*len(curr_player.seasons) +
                    update_player.perc_singles*len(update_player.seasons)) / num_seasons
    perc_doubles = (curr_player.perc_doubles * len(curr_player.seasons) +
                    update_player.perc_doubles * len(update_player.seasons)) / num_seasons
    perc_triples = (curr_player.perc_triples * len(curr_player.seasons) +
                    update_player.perc_triples * len(update_player.seasons)) / num_seasons
    perc_HR = (curr_player.perc_HR * len(curr_player.seasons) +
               update_player.perc_HR * len(update_player.seasons)) / num_seasons
    perc_walk = (curr_player.perc_walk * len(curr_player.seasons) +
                  update_player.perc_walk * len(update_player.seasons)) / num_seasons

    return Player(
        name=curr_player.name,
        seasons=sorted(set(curr_player.seasons + update_player.seasons)),
        true_BA=true_BA,
        perc_singles=perc_singles,
        perc_doubles=perc_doubles,
        perc_triples=perc_triples,
        perc_HR=perc_HR,
        perc_walk=perc_walk
    )
