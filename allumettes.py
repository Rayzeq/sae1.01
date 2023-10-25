from __future__ import annotations

import display
import terminal
from display import center
from scores import get_scores, set_scores
from terminal import bold, get_key

SCOREBOARD = "allumettes"


def add_score(winner: str, loser: str) -> None:
    scores: dict[str, list[float]]

    scores = dict(get_scores(SCOREBOARD))
    if winner not in scores:
        scores[winner] = [0, 0]
    if loser not in scores:
        scores[loser] = [0, 0]

    scores[winner][0] += 1
    scores[winner][1] += 1
    scores[loser][1] += 1

    set_scores(SCOREBOARD, scores.items())


def get_sorted_scores() -> list[tuple[str, str]]:
    score_lines: list[tuple[str, float]]
    player: str
    wins: float
    total: float
    winrate: float

    score_lines = []
    for player, (wins, total) in get_scores(SCOREBOARD):
        score_lines.append((player, wins / total * 100.0))

    score_lines.sort(key=lambda x: x[1], reverse=True)

    return [(player, f"{winrate:.2f}") for player, winrate in score_lines]


def game(player1: str, player2: str) -> None:
    matches: int
    playing: str
    waiting: str
    matches_display: list[tuple[int, int, str]]
    width: int
    height: int
    y: int

    width, height = terminal.get_size()
    y = height // 4 - 6 // 2

    matches = display.prompt_int(
        f"Avec quel nombre d'allumettes la partie va commencer (entre {bold(str(15))} et {bold(str(30))}) ?",
        15,
        30,
    )

    playing, waiting = player2, player1
    while matches > 0:
        playing, waiting = waiting, playing

        matches_display = [
            (center(2 * matches, width), y + 0, "▆ " * matches),
            (center(2 * matches, width), y + 1, "┃ " * matches),
            (center(2 * matches, width), y + 2, "┃ " * matches),
            (center(2 * matches, width), y + 3, "┃ " * matches),
            (center(2 * matches, width), y + 4, "┃ " * matches),
            (center(2 * matches, width), y + 5, "┃ " * matches),
        ]

        matches -= display.prompt_int(
            f"{bold(playing)}, combien voulez-vous prendre d'allumettes (entre {bold(str(1))} et {bold(str(3))}) ?",
            1,
            3,
            decorations=matches_display,
        )

    add_score(waiting, playing)

    display.screen(
        [f"{bold(waiting)} a gagné !!!"],
        keys={"ENTER": "Continuer"},
    )

    while get_key() != "\n":
        pass
