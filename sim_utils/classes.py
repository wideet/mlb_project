class Player:
    """
    Player class that represents the key statistics for each player
    """

    def __init__(self, name, num_seasons, true_BA, perc_singles, perc_doubles,
                 perc_triples, perc_HR, perc_walk):
        """
        Parameters
        ----------
        name: str
            player name
        num_seasons: int
            number of seasons recorded for player
        true_BA: float
            batting average per plate appearance (not at-bat)
        perc_singles: float
            percentage chance player hits a single, given they got a hit
        perc_doubles: float
            percentage chance player hits a double, given they got a hit
        perc_triples: float
            percentage chance player hits a triple, given they got a hit
        perc_HR: float
            percentage chance player hits a HR, given they got a hit
        perc_walk: float
            percentage chance player is walked per plate appearance
        """
        self.name = name
        self.num_seasons = num_seasons
        self.true_BA = true_BA
        self.perc_singles = perc_singles
        self.perc_doubles = perc_doubles
        self.perc_triples = perc_triples
        self.perc_HR = perc_HR
        self.perc_walk = perc_walk


class Team:
    """
    Team object consisting of a line-up of Players, and a record derived from
    the number games played and the number of wins the team has earned
    """

    def __init__(self, team_name, lineup=None, games_played=0, num_wins=0):
        """
        Parameters
        ----------
        team_name: str
            team name
        lineup: list
            list of Players
        games_played: int
            number of games played
        num_wins: int
            number of games won
        """
        self.name = team_name
        if not lineup:
            self.lineup = []
        else:
            self.lineup = lineup
        self.games_played = games_played
        self.num_wins = num_wins

    def get_winning_percentage(self):
        return self.num_wins / self.games_played

    def set_lineup(self, new_lineup):
        self.lineup = new_lineup

    def print_record(self):
        print(self.name, ': ', self.num_wins, '-', self.games_played - self.num_wins)


class Game:
    """
    Represents a single game, played between two teams
    """

    def __init__(self, away_team, home_team):
        """
        Parameters
        ----------
        away_team: Team
            away team object
        home_team: Team
            home team object
        """
        self.away_team = away_team
        self.home_team = home_team
        self.game_state = GameState()

    def print_game_score(self):
        print(self.away_team.name, ': ', self.game_state.score.away_team_score)
        print(self.home_team.name, ': ', self.game_state.score.home_team_score)


class Score:
    """
    Score object to keep track of the score in a Game
    """

    def __init__(self):
        """
        Default to score of 0-0
        """
        self.away_team_score = 0
        self.home_team_score = 0

    def update_score(self, bottom, num_runs):

        if bottom:
            self.home_team_score += num_runs
        else:
            self.away_team_score += num_runs

    def print_score(self):
        print(self.away_team_score, '-', self.home_team_score)

    def get_score(self):
        return str(self.away_team_score) + '-' + str(self.home_team_score)


class GameState:
    # TODO: Add batter, pitcher? #
    """
    Class to keep track of state of a particular Game
    """

    def __init__(self, inning=1, bottom=False, outs=0, score=Score,
                 first_base=False, second_base=False, third_base=False):
        """
        Parameters
        ----------
        inning: int
            current inning in Game
        bottom: bool
            indicator whether game is in bottom of inning
        outs: int
            number of outs in the inning
        score: class
            current Game Score
        first_base: bool
            indicator whether there is a man on first
        second_base: bool
            indicator whether there is a man on second
        third_base: bool
            indicator whether there is a man on third
        """

        self.inning = inning
        self.bottom = bottom
        self.outs = outs
        self.score = score()

        self.base_ls = [first_base, second_base, third_base]

    def print_state(self):

        print('Inning: ', self.inning)
        print('Bottom of Inning: ', self.bottom)
        print('Score: ', self.score.get_score())
        print('Outs: ', self.outs)

        print('First Base: ', self.base_ls[0])
        print('Second Base: ', self.base_ls[1])
        print('Third Base: ', self.base_ls[2])

    def update_base_ls(self, first_base_status, second_base_status, third_base_status):
        self.base_ls = [first_base_status, second_base_status, third_base_status]

    def update_state(self, event):
        """
        Update the GameState given theoretical idea of consequences of certain
        events in different circumstances

        Parameters
        ----------
        event

        Returns
        -------

        """

        num_MOB = len([base for base in self.base_ls if base])
        num_runs = 0

        if event == 'out':
            self.outs += 1
            if self.outs == 3:
                if self.bottom:
                    self.inning += 1
                self.bottom = bool(1 - int(self.bottom))
                self.outs = 0
                self.update_base_ls(False, False, False)


        elif event == 'walk':
            if num_MOB == 3:
                num_runs = 1

            else:
                if not self.base_ls[0]:
                    self.base_ls[0] = True
                elif not self.base_ls[1]:
                    self.base_ls[1] = True
                else:
                    self.base_ls[2] = True

        elif event == 4:
            num_runs = num_MOB + 1
            self.update_base_ls(False, False, False)

        elif event == 3:
            num_runs = num_MOB
            self.update_base_ls(False, False, True)

        elif event == 2:
            num_runs = int(self.base_ls[1]) + int(self.base_ls[2])
            self.update_base_ls(False, True, self.base_ls[0])

        elif event == 1:
            num_runs = int(self.base_ls[1]) + int(self.base_ls[2])
            self.update_base_ls(True, self.base_ls[0], False)

        self.score.update_score(self.bottom, num_runs=num_runs)
