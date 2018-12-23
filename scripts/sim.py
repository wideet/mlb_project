import sys
sys.path.append('../')
from sim_utils.utils import *

from collections import defaultdict
import numpy as np
import copy
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
    home_lineup = copy.deepcopy(game.home_team.lineup)
    away_lineup = copy.deepcopy(game.away_team.lineup)

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
        game.game_state.update_state(PA_result)

    # game.print_team_score()
    if game.game_state.score.home_team_score > \
            game.game_state.score.away_team_score:
        # print("HOME TEAM WINS!")
        game.home_team.num_wins += 1
    else:
        # print("AWAY TEAM WINS!")
        game.away_team.num_wins += 1

    game.home_team.games_played += 1
    game.away_team.games_played += 1


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


if __name__ == '__main__':

    n_iterations = 10

    team_wins_dict = defaultdict(lambda: 0, {})
    training_years = {2017, 2018}
    roster_year = 2017
    schedule_year = 2018
    player_dict = defaultdict(lambda: None, {})
    for train_year in training_years:
        batting_df = get_player_batting_df(train_year)
        for index, row in batting_df.iterrows():
            row_player = create_player_from_row(row)
            # noinspection PyTypeChecker
            player_dict[row_player.name] = update_player(
                player_dict[row_player.name], row_player)

    team_dict = {}
    roster_year_batting_df = get_player_batting_df(roster_year)
    for index, row in roster_year_batting_df.iterrows():
        player_team = row['Team Name']
        player_name = row['Name']
        if player_team not in team_dict:
            team_dict[player_team] = Team(player_team)
        team_dict[player_team].lineup.append(player_dict[player_name])

    # sort lineups by .... true_BA?

    #####

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
