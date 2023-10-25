from __future__ import annotations

import display
import terminal
from scores import get_scores, set_scores
from terminal import bold, get_key, invert, strip_escapes

SCOREBOARD = "morpion"


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


def display_grid(message: str, grid: list[list[str]]) -> None:
    LINE_LENGHT: int = 11

    line: list[str]
    lines: list[str] = []

    for line in grid:
        lines.append("│".join(line))
        lines.append("───┼───┼───")

    lines.pop()
    display.screen(lines, keys={"ENTER": "Valider", "↑ / ↓ / → / ←": "Choisir une case"})

    # here the cursor is at the end of the last line of the grid
    terminal.cursor_up(6)
    terminal.cursor_left(len(strip_escapes(message)) // 2 + LINE_LENGHT // 2)
    print(message, end="", flush=True)


def place_symbol(player: str, symbol: str, grid: list[list[str]]) -> None:
    key: str
    sel_x: int = 1
    sel_y: int = 1

    while True:
        grid[sel_y][sel_x] = invert(grid[sel_y][sel_x])
        display_grid(f"{bold(player)}, à toi de jouer !", grid)
        grid[sel_y][sel_x] = strip_escapes(grid[sel_y][sel_x])

        key = get_key()
        if key == "UP":
            sel_y = max(0, sel_y - 1)
        elif key == "DOWN":
            sel_y = min(2, sel_y + 1)
        elif key == "LEFT":
            sel_x = max(0, sel_x - 1)
        elif key == "RIGHT":
            sel_x = min(2, sel_x + 1)
        elif key == "\n" and grid[sel_y][sel_x] == "   ":
            break

    grid[sel_y][sel_x] = f" {symbol} "


def check_win(grid: list[list[str]]) -> str:
    line: list[str]
    x: int

    for line in grid:
        if line[0] == line[1] == line[2]:
            return line[0].strip()

    for x in range(3):
        if grid[0][x] == grid[1][x] == grid[2][x]:
            return grid[0][x].strip()

    if grid[0][0] == grid[1][1] == grid[2][2]:
        return grid[0][0].strip()

    if grid[0][2] == grid[1][1] == grid[2][0]:
        return grid[0][2].strip()

    return ""


def game(player1: str, player2: str) -> None:
    grid: list[list[str]]
    playing: str
    waiting: str
    winner: str
    loser: str

    grid = [
        ["   ", "   ", "   "],
        ["   ", "   ", "   "],
        ["   ", "   ", "   "],
    ]
    playing, waiting = player2, player1

    while True:
        playing, waiting = waiting, playing

        if playing == player1:
            place_symbol(playing, "×", grid)
        else:
            place_symbol(playing, "○", grid)

        winner = check_win(grid)
        if winner != "":
            break

    winner, loser = (player1, player2) if winner == "×" else (player2, player1)
    add_score(winner, loser)

    display.screen(
        [f"{bold(winner)} a gagné !!!"],
        keys={"ENTER": "Continuer"},
    )

    while get_key() != "\n":
        pass
