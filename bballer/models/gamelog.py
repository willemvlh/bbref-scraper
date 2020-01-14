from datetime import date

class GameLog:
    date: date
    team: str
    age: str
    opponent: str
    played: bool
    started: bool
    seconds_played: int
    result: str
    fg_made: int
    fg_attempted: int
    three_fg_made: int
    three_fg_attempted: int
    ft_made: int
    ft_attempted: int
    offensive_rebounds: int
    defensive_rebounds: int
    assists: int
    steals: int
    blocks: int
    turnovers: int
    fouls: int
    game_score: float
    plus_minus: int
    points: int

    def __repr__(self):
        return f"GameLog(points={self.points}, rebounds={self.rebounds}, assists={self.assists})"

    @property
    def rebounds(self):
        return self.offensive_rebounds + self.defensive_rebounds