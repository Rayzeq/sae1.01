from __future__ import annotations

import time

import display
import terminal
from display import center
from scores import get_scores, set_scores
from terminal import bold, get_key, strip_escapes

SCOREBOARD = "pow4"
RULES = []


def add_score(winner: str, loser: str, *, tie: bool = False) -> None:
    """Met à jour le score des deux joueurs dans la base de donnée.

    Le gagnant se voit ajouter une victoire et les deux joueurs se voient ajouter une partie jouée.
    Si `tie` est vrai, alors aucun joueur ne voit son nombre de victoires augmenter.

    :param winner: Le nom du gagnant
    :param loser:  Le nom du perdant
    :param tie:    Vrai si la partie s'est terminée par une égalité.
    """
    scores: dict[str, list[float]]

    scores = dict(get_scores(SCOREBOARD))
    if winner not in scores:
        scores[winner] = [0, 0]
    if loser not in scores:
        scores[loser] = [0, 0]

    if not tie:
        scores[winner][0] += 1
    scores[winner][1] += 1
    scores[loser][1] += 1

    set_scores(SCOREBOARD, scores.items())


def get_sorted_scores() -> list[tuple[str, str]]:
    """Retourne les scores triés par ordre décroissant (un score plus grand est meilleur).

    Le score d'un joueur représente son pourcentage de victoires.

    :returns: Les scores triés.
    :rtype:   Une liste de tuples (nom du joueur, score).
    """
    score_lines: list[tuple[str, float]]
    player: str
    wins: float
    total: float
    winrate: float
    x: tuple[str, float]

    score_lines = []
    for player, (wins, total) in get_scores(SCOREBOARD):
        score_lines.append((player, wins / total * 100.0))

    score_lines.sort(key=lambda x: x[1], reverse=True)

    return [(player, f"{winrate:.2f}") for player, winrate in score_lines]


def display_grid(grid: list[list[str]]) -> None:
    line: list[str]
    lines: list[str] = []

    for line in grid:
        lines.append("│" + "│".join(line) + "│")

    lines.append("└─┴─┴─┴─┴─┴─┴─┘")

    display.screen(lines, keys={"ENTER": "Valider", "← / →": "Choisir une case"})


def drop_token(x: int, color: str, grid: list[list[str]]) -> None:
    DELAY: float = 0.2
    y: int = 0

    grid[y][x] = f"{color}⬤\x1b[0m"
    display_grid(grid)
    time.sleep(DELAY)

    while y < 5 and grid[y + 1][x] == " ":
        grid[y][x] = " "
        grid[y + 1][x] = f"{color}⬤\x1b[0m"
        display_grid(grid)
        time.sleep(DELAY)
        y += 1

    grid[y][x] = f"{color}⬤\x1b[0m"


def place_token(player: str, color: str, grid: list[list[str]]) -> None:
    key: str
    sel_x: int = 3
    msg: str
    width: int

    width, _ = terminal.get_size()

    while True:
        display_grid(grid)
        msg = f"{bold(player)}, à toi de jouer !"

        # here the cursor is at the end of the last line of the grid
        terminal.cursor_up(7)
        terminal.cursor_left(14 - sel_x * 2)
        print(f"{color}⬤\x1b[0m", end="", flush=True)

        terminal.cursor_up(2)
        terminal.set_cursor_x(center(len(strip_escapes(msg)), width))
        print(msg, end="", flush=True)

        key = get_key()
        if key == "LEFT":
            sel_x = (sel_x - 1) % 7
        elif key == "RIGHT":
            sel_x = (sel_x + 1) % 7
        elif key == "\n" and grid[0][sel_x] == " ":
            break

    drop_token(sel_x, color, grid)


def check_win(grid: list[list[str]]) -> str:
    x: int
    y: int
    token: str

    for y in range(6):
        for x in range(4):
            if grid[y][x] == grid[y][x + 1] == grid[y][x + 2] == grid[y][x + 3] != " ":
                return grid[y][x]

    for y in range(3):
        for x in range(7):
            if grid[y][x] == grid[y + 1][x] == grid[y + 2][x] == grid[y + 3][x] != " ":
                return grid[y][x]

    for y in range(3):
        for x in range(4):
            if grid[y][x] == grid[y + 1][x + 1] == grid[y + 2][x + 2] == grid[y + 3][x + 3] != " ":
                return grid[y][x]

    for y in range(3):
        for x in range(4):
            if grid[y + 3][x] == grid[y + 2][x + 1] == grid[y + 1][x + 2] == grid[y][x + 3] != " ":
                return grid[y + 3][x]

    if all(all(token != " " for token in line) for line in grid):
        return "t"

    return ""


def game(player1: str, player2: str) -> None:
    grid: list[list[str]]
    playing: str
    waiting: str
    winner: str
    loser: str

    grid = [
        [" ", " ", " ", " ", " ", " ", " "],
        [" ", " ", " ", " ", " ", " ", " "],
        [" ", " ", " ", " ", " ", " ", " "],
        [" ", " ", " ", " ", " ", " ", " "],
        [" ", " ", " ", " ", " ", " ", " "],
        [" ", " ", " ", " ", " ", " ", " "],
    ]
    playing, waiting = player2, player1

    while True:
        playing, waiting = waiting, playing

        if playing == player1:
            place_token(playing, "\x1b[31m", grid)
        else:
            place_token(playing, "\x1b[33m", grid)

        winner = check_win(grid)
        if winner != "":
            break

    if winner == "t":
        add_score(player1, player2, tie=True)

        display.screen(
            ["Égalité !!!"],
            keys={"ENTER": "Continuer"},
        )
    else:
        winner, loser = (player1, player2) if winner == "\x1b[31m⬤\x1b[0m" else (player2, player1)
        add_score(winner, loser)

        display.screen(
            [f"{bold(winner)} a gagné !!!"],
            keys={"ENTER": "Continuer"},
        )

    while get_key() != "\n":
        pass
