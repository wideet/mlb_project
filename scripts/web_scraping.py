from bs4 import BeautifulSoup
import requests
import pandas as pd


# Adjust the scraping so that it only gets regular season games
def get_schedule(year):
    schedule = []

    url = 'https://www.baseball-reference.com/leagues/MLB/' + str(year) + '-schedule.shtml'
    schedule_page = requests.get(url)

    soup = BeautifulSoup(schedule_page.text, 'html.parser')
    games = soup.find_all(class_='game')

    for game in games:
        if game.find('span') != None:
            continue
        teams = game.find_all('a')
        away_team = teams[0].text
        home_team = teams[1].text

        schedule.append((away_team, home_team))

    return (year, schedule)


# will take some doing...
# need the correct values for attributes of a Player class
# and need to aggregate them to the correct team in a list
# sort by top 9 batters

def get_player_batting_df(year):

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

    # Get the player data from web scraper
    # df = pd.DataFrame()
    #
    # url = 'https://www.baseball-reference.com/leagues/MLB/' + str(year) + '-standard-batting.shtml'
    # batting_page = requests.get(url)
    #
    # session = HTMLSession()
    # r = session.get(url)
    # r.html.render(retries=1)
    #
    # soup = BeautifulSoup(r.html.text, 'html.parser')
    #
    # print(soup)




    df = pd.read_csv('C:/Users/Wideet/Desktop/MLB_Data/' + str(year) + '_batting.csv')
    # Let's assume we got everything....

    # Preprocess to more easily aggregate to team rosters
    df['Team Name'] = df['Tm'].apply(lambda x: abbreviations[x] if x in abbreviations else None)
    df['Name'] = df['Name'].apply(lambda x: x.split('\\')[0]).replace('*', '').replace('#','')

    roster_indices = list(df.groupby('Tm')['PA'].nlargest(9).reset_index()['level_1'].values)
    roster_df = df.iloc[roster_indices]
    roster_df = roster_df[roster_df['Tm'].isin(abbreviations)]

    return roster_df

get_player_batting_df(2018)


