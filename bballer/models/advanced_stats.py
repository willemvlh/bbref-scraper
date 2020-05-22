from dataclasses import dataclass, field


@dataclass
class AdvancedStatLine:
    season: int
    player_efficiency_rating: float
    true_shooting_percentage: float
    three_fg_attempt_rate: float
    ft_attempt_rate: float
    offensive_rebound_percentage: float
    defensive_rebound_percentage: float
    total_rebound_percentage: float
    assist_percentage: float
    steal_percentage: float
    block_percentage: float
    turnover_percentage: float
    usage_percentage: float
    offensive_win_shares: float
    defensive_win_shares: float
    win_shares_per_48: float
    offensive_box_plus_minus: float
    defensive_box_plus_minus: float
    value_over_replacement_player: float
    box_plus_minus: float = field(init=False)
    win_shares: float = field(init=False)

    def __repr__(self):
        return f"AdvancedStatLine({self.season})"

    def __post_init__(self):
        if self.defensive_box_plus_minus and self.offensive_box_plus_minus:
            self.box_plus_minus = self.defensive_box_plus_minus + self.offensive_box_plus_minus
        if self.offensive_win_shares and self.defensive_win_shares:
            self.win_shares = self.offensive_win_shares + self.defensive_win_shares
