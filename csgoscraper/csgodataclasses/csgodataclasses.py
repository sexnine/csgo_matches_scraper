from dataclasses import dataclass


@dataclass
class PlayerStats:
    ping: int
    kills: int
    assists: int
    deaths: int
    mvps: int
    headshot_rate: int
    score: int


@dataclass
class Player:
    name: str
    link: str
    stats: PlayerStats


@dataclass
class Team:
    players: list
    score: int


@dataclass
class Match:
    name: str
    time: str
    ranked: bool
    wait_time: int
    duration: int
    teams: list