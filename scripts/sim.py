import sys
sys.path.append('../')
from sim_utils.utils import *

from collections import defaultdict
import numpy as np
import copy
import argparse
import pprint

pp = pprint.PrettyPrinter(indent=4)


def simulate_game(game):
    """
    Simulate a game

    Parameters
    ----------
    game: Game
        Game object

    Returns
    -------

    """
    home_lineup = copy.copy(game.home_team.lineup)
    away_lineup = copy.copy(game.away_team.lineup)

    while game.game_state.inning <= 9 or \
            game.game_state.score.home_team_score == \
            game.game_state.score.away_team_score:

        if game.game_state.inning >= 9 and \
                game.game_state.bottom and \
                game.game_state.score.home_team_score > \
                game.game_state.score.away_team_score:
            break

        if game.game_state.bottom:
            lineup = home_lineup
        else:
            lineup = away_lineup

        if len(lineup) > 0:
            curr_player = lineup.pop(0)
            lineup.append(curr_player)

        PA_result = np.random.choice(
            [
                "hit", "walk", "out"
            ],
            p=
            [
                curr_player.true_BA,
                curr_player.perc_walk,
                (1 - curr_player.true_BA - curr_player.perc_walk)
            ]
        )

        if PA_result == 'hit':
            PA_result = np.random.choice(
                [
                    1, 2, 3, 4
                ],
                p=
                [
                    curr_player.perc_singles,
                    curr_player.perc_doubles,
                    curr_player.perc_triples,
                    curr_player.perc_HR
                ]
            )

        curr_player.update_curr_sim_stats(PA_result)
        game.game_state.update_state(PA_result)

    # game.print_team_score()
    if game.game_state.score.home_team_score > \
            game.game_state.score.away_team_score:
        game.home_team.num_wins += 1
    else:
        game.away_team.num_wins += 1

    game.home_team.games_played += 1
    game.away_team.games_played += 1
    game.reset()


def simulate_season(schedule):
    """
    Simulate a single season with a given list of Games

    Parameters
    ----------
    schedule: list
        list of Game objects

    Returns
    -------

    """

    for game in schedule:
        simulate_game(game)


# TODO: Add player logging for each iteration / season
#  want to see if player performance is accurate
# Possible y-value in a modeling scenario: WAR / game played?


def sim():

    parser = argparse.ArgumentParser(description="Simulate with given "
                                                 "instructions")
    parser.add_argument('--n', '--n_iterations', dest='n_iterations',
                        type=int,
                        help='number of iterations of complete seasons to '
                             'simulate and average over',
                        required=False,
                        default=10)
    args = parser.parse_args()

    n_iterations = args.n_iterations
    team_wins_dict = defaultdict(lambda: 0, {})
    training_years = {2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017}
    roster_year = 2018
    schedule_year = 2018
    player_dict = defaultdict(lambda: None, {})
    default_value_dict = defaultdict(lambda: 0, {})

    for train_year in training_years:
        batting_df = get_player_batting_df(train_year)
        for index, row in batting_df.iterrows():
            row_player = create_player_from_row(row, train_year)
            # noinspection PyTypeChecker
            player_dict[row_player.name] = update_player(
                player_dict[row_player.name], row_player)

            # update default value dictionary
            default_value_dict['PA'] += row['PA']
            default_value_dict['H'] += row['H']
            default_value_dict['2B'] += row['2B']
            default_value_dict['3B'] += row['3B']
            default_value_dict['HR'] += row['HR']
            default_value_dict['1B'] += row['H'] - (
                        row['2B'] + row['3B'] + row['HR'])
            default_value_dict['BB'] += row['BB'] + row['IBB'] + row['HBP']

    for key in default_value_dict:
        default_value_dict[key] = default_value_dict[key] / \
                                  (len(training_years) * 270)

    team_dict = {}
    roster_year_batting_df = get_player_batting_df(roster_year)
    for index, row in roster_year_batting_df.iterrows():
        player_team = row['Team Name']
        player_name = row['Name']
        if player_team not in team_dict:
            team_dict[player_team] = Team(player_team)
        team_dict[player_team].add_player(player_dict, player_name,
                                          default_value_dict)
    # sort lineups by .... true_BA?
    for team, value in team_dict.items():
        value.sort_lineup()

    _, schedule = get_schedule(schedule_year)
    mod_schedule = []
    for tup in schedule:
        game = Game(team_dict[tup[0]], team_dict[tup[1]])
        mod_schedule.append(game)

    for i in range(n_iterations):
        print(i)

        simulate_season(
            schedule=mod_schedule,
        )

        for team_name, team in team_dict.items():
            team_wins = team.num_wins
            team_wins_dict[team_name] += team_wins

            team.num_wins = 0
            team.games_played = 0

    for key, value in team_wins_dict.items():
        team_wins_dict[key] = value / n_iterations

    pp.pprint(sorted(team_wins_dict.items(), key=lambda x: x[1], reverse=True))
    top_team = sorted(team_wins_dict.items(), key=lambda x: x[1], reverse=True)[0][0]
    for player in team_dict[top_team].lineup:
        pp.pprint (player.name)
        pp.pprint(player.curr_sim)
        pp.pprint(player.to_dict())


if __name__ == '__main__':
    sim()
