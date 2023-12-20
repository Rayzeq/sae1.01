from __future__ import annotations

import random
from random import randint

import display
import terminal
from players import difficulty_level, get_display_name
from scores import get_scores, set_scores
from terminal import bold, get_key, invert, strip_escapes

SCOREBOARD = "morpion"
RULES = [
    "L'objectif est de mettre trois fois son symbole de suite (× ou ○) dans une grille de 3 par 3.",
    "Pour ce faire vous allez placer votre symbole dans une case inoccupée chacun votre tour.",
    "Une ligne peut être horizontale, verticale, ou diagonale.",
]


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
    if winner[0] != "\t" and winner not in scores:
        scores[winner] = [0, 0]
    if loser[0] != "\t" and loser not in scores:
        scores[loser] = [0, 0]

    if winner[0] != "\t":
        if not tie:
            scores[winner][0] += 1
        scores[winner][1] += 1
    if loser[0] != "\t":
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


def display_grid(message: str, grid: list[list[str]], *, keys: dict[str, str] | None = None) -> None:
    """Affiche la grille du jeu.

    :param message: Un message à afficher au dessus de la grille
    :param grid:    La grille en elle-même
    """
    LINE_LENGHT: int = 11

    line: list[str]
    lines: list[str] = []

    if keys is None:
        keys = {"ENTER": "Valider", "↑ / ↓ / → / ←": "Choisir une case"}

    for line in grid:
        lines.append("│".join(line))
        lines.append("───┼───┼───")

    lines.pop()
    display.screen(lines, keys=keys)

    # here the cursor is at the end of the last line of the grid
    terminal.cursor_up(6)
    terminal.cursor_left(len(strip_escapes(message)) // 2 + LINE_LENGHT // 2)
    print(message, end="", flush=True)


def place_symbol(player: str, symbol: str, grid: list[list[str]]) -> None:
    """Demande au joueur `player` de placer son symbole `symbol` dans la grille.

    :param player: Le joueur qui doit placer son symbol
    :param symbol: Le symbole qui correspond à ce joueur (× ou ○)
    :param grid:   La grille de jeu
    """
    key: str
    sel_x: int = 1
    sel_y: int = 1

    while True:
        grid[sel_y][sel_x] = invert(grid[sel_y][sel_x])
        display_grid(f"{bold(player)}, à toi de jouer !", grid)
        grid[sel_y][sel_x] = strip_escapes(grid[sel_y][sel_x])

        key = get_key()
        if key == "UP":
            sel_y = (sel_y - 1) % 3
        elif key == "DOWN":
            sel_y = (sel_y + 1) % 3
        elif key == "LEFT":
            sel_x = (sel_x - 1) % 3
        elif key == "RIGHT":
            sel_x = (sel_x + 1) % 3
        elif key == "\n" and grid[sel_y][sel_x] == "   ":
            break

    grid[sel_y][sel_x] = f" {symbol} "


def check_win(grid: list[list[str]]) -> str:
    """Vérifie si un joueur a gagné.

    :param grid: La grille de jeu
    :returns:    Cette fonction retourne:
        - "×" ou "○" si un joueur a gagné
        - "t" si la partie s'est terminée par une égalité
        - "" si la partie n'est pas terminée
    """
    line: list[str]
    x: int
    symbol: str

    # check lines
    for line in grid:
        if line[0] == line[1] == line[2] != "   ":
            return line[0].strip()

    # check columns
    for x in range(3):
        if grid[0][x] == grid[1][x] == grid[2][x] != "   ":
            return grid[0][x].strip()

    # check diagonals
    if grid[0][0] == grid[1][1] == grid[2][2] != "   ":
        return grid[0][0].strip()

    if grid[0][2] == grid[1][1] == grid[2][0] != "   ":
        return grid[0][2].strip()

    if all(all(symbol != "   " for symbol in line) for line in grid):
        return "t"

    return ""


def check_possible_win(grid: list[list[str]], symbol: str) -> tuple[int, int] | None:
    for y in range(3):
        if grid[y][0] == grid[y][1] == f" {symbol} " and grid[y][2] == "   ":
            return 2, y
    for y in range(3):
        if grid[y][1] == grid[y][2] == f" {symbol} " and grid[y][0] == "   ":
            return 0, y
    for y in range(3):
        if grid[y][0] == grid[y][2] == f" {symbol} " and grid[y][1] == "   ":
            return 1, y

    for x in range(3):
        if grid[0][x] == grid[1][x] == f" {symbol} " and grid[2][x] == "   ":
            return x, 2
    for x in range(3):
        if grid[1][x] == grid[2][x] == f" {symbol} " and grid[0][x] == "   ":
            return x, 0
    for x in range(3):
        if grid[0][x] == grid[2][x] == f" {symbol} " and grid[1][x] == "   ":
            return x, 1

    if grid[0][0] == grid[1][1] == f" {symbol} " and grid[2][2] == "   ":
        return 2, 2
    if grid[1][1] == grid[2][2] == f" {symbol} " and grid[0][0] == "   ":
        return 0, 0
    if grid[0][0] == grid[2][2] == f" {symbol} " and grid[1][1] == "   ":
        return 1, 1

    if grid[0][2] == grid[1][1] == f" {symbol} " and grid[2][0] == "   ":
        return 0, 2
    if grid[1][1] == grid[2][0] == f" {symbol} " and grid[0][2] == "   ":
        return 2, 0
    if grid[0][2] == grid[2][0] == f" {symbol} " and grid[1][1] == "   ":
        return 1, 1

    return None


def auto_play(bot_name: str, symbol: str, ennemy_symbol: str, grid: list[list[str]]) -> tuple[int, int]:
    diff_level = difficulty_level(bot_name)

    if diff_level == 1:  # niveau de difficulté moyen
        # le bot à 1 chance sur 2 d'être en mode "difficile"
        diff_level = random.choice((0, 2))

    if diff_level == 0:  # niveau de difficulté facile
        x, y = randint(0, 2), randint(0, 2)
        while grid[y][x] != "   ":
            x, y = randint(0, 2), randint(0, 2)
        return x, y
    else:  # niveau de difficulté difficile
        # ici le bot ne joue pas toujours le meilleur coup car il est difficile à determiner
        win_pos = check_possible_win(grid, symbol)
        if win_pos:
            return win_pos

        ennemy_win_pos = check_possible_win(grid, ennemy_symbol)
        if ennemy_win_pos:
            return ennemy_win_pos

        x, y = randint(0, 2), randint(0, 2)
        while grid[y][x] != "   ":
            x, y = randint(0, 2), randint(0, 2)

        return x, y


def game(player1: str, player2: str) -> None:
    """Lance une partie de morpion et sauvegarde le score à la fin de la partie.

    :param player1: Le nom du joueur 1 (celui qui commence)
    :param player2: Le nom du joueur 2
    """
    grid: list[list[str]]
    playing: str
    waiting: str
    winner: str
    loser: str
    symbol: str
    x: int
    y: int

    grid = [
        ["   ", "   ", "   "],
        ["   ", "   ", "   "],
        ["   ", "   ", "   "],
    ]
    playing, waiting = player2, player1

    while True:
        playing, waiting = waiting, playing

        symbol = "×" if playing == player1 else "○"
        if playing[0] == "\t":
            x, y = auto_play(playing, symbol, "○" if playing == player1 else "×", grid)
            grid[y][x] = f" {symbol} "

            display_grid(f"{bold(get_display_name(playing))} a joué !", grid, keys={"ENTER": "Continuer"})
            while get_key() != "\n":
                pass
        else:
            place_symbol(playing, symbol, grid)

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
        winner, loser = (player1, player2) if winner == "×" else (player2, player1)
        add_score(winner, loser)

        display.screen(
            [f"{bold(get_display_name(winner))} a gagné !!!"],
            keys={"ENTER": "Continuer"},
        )

    while get_key() != "\n":
        pass
