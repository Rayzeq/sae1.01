from __future__ import annotations

from typing import Dict, List, Tuple

import display
import terminal
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
    scores: Dict[str, List[float]]

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


def get_sorted_scores() -> List[Tuple[str, str]]:
    """Retourne les scores triés par ordre décroissant (un score plus grand est meilleur).

    Le score d'un joueur représente son pourcentage de victoires.

    :returns: Les scores triés.
    :rtype:   Une liste de tuples (nom du joueur, score).
    """
    score_lines: List[Tuple[str, float]]
    player: str
    wins: float
    total: float
    winrate: float
    x: Tuple[str, float]

    score_lines = []
    for player, (wins, total) in get_scores(SCOREBOARD):
        score_lines.append((player, wins / total * 100.0))

    score_lines.sort(key=lambda x: x[1], reverse=True)

    return [(player, f"{winrate:.2f}") for player, winrate in score_lines]


def display_grid(message: str, grid: List[List[str]]) -> None:
    """Affiche la grille du jeu.

    :param message: Un message à afficher au dessus de la grille
    :param grid:    La grille en elle-même
    """
    LINE_LENGHT: int = 11

    line: List[str]
    lines: List[str] = []

    for line in grid:
        lines.append("│".join(line))
        lines.append("───┼───┼───")

    lines.pop()
    display.screen(lines, keys={"ENTER": "Valider", "↑ / ↓ / → / ←": "Choisir une case"})

    # here the cursor is at the end of the last line of the grid
    terminal.cursor_up(6)
    terminal.cursor_left(len(strip_escapes(message)) // 2 + LINE_LENGHT // 2)
    print(message, end="", flush=True)


def place_symbol(player: str, symbol: str, grid: List[List[str]]) -> None:
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


def check_win(grid: List[List[str]]) -> str:
    """Vérifie si un joueur a gagné.

    :param grid: La grille de jeu
    :returns:    Cette fonction retourne:
        - "×" ou "○" si un joueur a gagné
        - "t" si la partie s'est terminée par une égalité
        - "" si la partie n'est pas terminée
    """
    line: List[str]
    x: int
    symbol: str

    for line in grid:
        if line[0] == line[1] == line[2] != "   ":
            return line[0].strip()

    for x in range(3):
        if grid[0][x] == grid[1][x] == grid[2][x] != "   ":
            return grid[0][x].strip()

    if grid[0][0] == grid[1][1] == grid[2][2] != "   ":
        return grid[0][0].strip()

    if grid[0][2] == grid[1][1] == grid[2][0] != "   ":
        return grid[0][2].strip()

    if all(all(symbol != "   " for symbol in line) for line in grid):
        return "t"

    return ""


def game(player1: str, player2: str) -> None:
    """Lance une partie de morpion et sauvegarde le score à la fin de la partie.

    :param player1: Le nom du joueur 1 (celui qui commence)
    :param player2: Le nom du joueur 2
    """
    grid: List[List[str]]
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
            [f"{bold(winner)} a gagné !!!"],
            keys={"ENTER": "Continuer"},
        )

    while get_key() != "\n":
        pass
