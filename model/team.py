from dataclasses import dataclass


@dataclass
class Team:
    name: str
    url: str
    is_conference: bool