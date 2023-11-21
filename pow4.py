from __future__ import annotations

import time

import display
import terminal
from display import center
from scores import get_scores, set_scores
from terminal import bold, get_key, strip_escapes

SCOREBOARD = "pow4"
RULES = [
    "L'objectif est d'aligner 4 jetons de sa couleur dans une grille de 7 par 6.",
    "Pour ce faire vous allez placer votre jeton dans une colonne non remplie chacun votre tour.",
    "Une ligne peut être horizontale, verticale, ou diagonale.",
    "Le premier joueur à aligner 4 jetons de sa couleur gagne la partie.",
    "Si la grille est remplie sans qu'aucun joueur n'ait aligné 4 jetons, la partie se termine par une égalité.",
]
P1_COLOR = "31"
P2_COLOR = "93"
GRID_WIDTH = 7
GRID_HEIGHT = 6
TOKEN = "⬤"


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
    """Affiche la "grille" du jeu.

    :param grid:    La grille du jeu
    """
    line: list[str]
    lines: list[str] = []

    for line in grid:
        lines.append("│" + "│".join(line) + "│")

    lines.append("└─┴─┴─┴─┴─┴─┴─┘")

    display.screen(lines, keys={"ENTER": "Valider", "← / →": "Choisir une case"})


def make_token(color: str) -> str:
    """Renvoie un jeton coloré.

    :param color: Le code de la couleur du jeton en séquence d'échappement ANSI
    """
    return f"\x1b[{color}m{TOKEN}\x1b[0m"


def drop_token(x: int, color: str, grid: list[list[str]]) -> None:
    """Fait tomber un jeton dans la colonne `x` de la grille `grid`.

    Cette fonction joue une animation pour faire tomber le jeton ET modifie la grille.

    :param x:     La colonne dans laquelle le jeton doit être placé
    :param color: La couleur du jeton
    :param grid:  La grille de jeu
    """
    DELAY: float = 0.2
    y: int = 0

    grid[y][x] = make_token(color)
    display_grid(grid)
    time.sleep(DELAY)

    while y < GRID_HEIGHT - 1 and grid[y + 1][x] == " ":
        grid[y][x] = " "
        grid[y + 1][x] = make_token(color)
        display_grid(grid)
        time.sleep(DELAY)
        y += 1

    grid[y][x] = make_token(color)
    # ignore toutes les touches appuyées pendant les time.sleep()
    terminal.flush_stdin()


def place_token(player: str, color: str, grid: list[list[str]]) -> None:
    """Demande au joueur `player` de placer un jeton dans la grille.

    :param player: Le joueur qui doit placer un jeton
    :param color:  La couleur du jeton
    :param grid:   La grille de jeu
    """
    key: str
    sel_x: int = 3
    msg: str
    width: int

    width, _ = terminal.get_size()

    while True:
        display_grid(grid)
        msg = f"{bold(player)}, à toi de jouer !"

        # here the cursor is at the end of the last line of the grid
        terminal.cursor_up(GRID_HEIGHT + 1)
        terminal.cursor_left(GRID_WIDTH * 2 - sel_x * 2)
        print(make_token(color), end="", flush=True)

        terminal.cursor_up(2)
        terminal.set_cursor_x(center(len(strip_escapes(msg)), width))
        print(msg, end="", flush=True)

        key = get_key()
        if key == "LEFT":
            sel_x = (sel_x - 1) % GRID_WIDTH
        elif key == "RIGHT":
            sel_x = (sel_x + 1) % GRID_WIDTH
        elif key == "\n" and grid[0][sel_x] == " ":
            break

    drop_token(sel_x, color, grid)


def check_win(grid: list[list[str]]) -> str:
    r"""Vérifie si un joueur a gagné.

    :param grid: La grille de jeu
    :returns:    Cette fonction retourne:
        - le jeton du joueur qui a gagné si un joueur à gagné ("\x1b[31m⬤\x1b[0m" ou "\x1b[93m⬤\x1b[0m")
        - "t" si la partie s'est terminée par une égalité
        - "" si la partie n'est pas terminée
    """
    x: int
    y: int
    token: str

    # vérifie les lignes
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH - 3):
            if grid[y][x] == grid[y][x + 1] == grid[y][x + 2] == grid[y][x + 3] != " ":
                return grid[y][x]

    # vérifie les colonnes
    for y in range(GRID_HEIGHT - 3):
        for x in range(GRID_WIDTH):
            if grid[y][x] == grid[y + 1][x] == grid[y + 2][x] == grid[y + 3][x] != " ":
                return grid[y][x]

    # vérifie les diagonales (haut-gauche vers bas-droite)
    for y in range(GRID_HEIGHT - 3):
        for x in range(GRID_WIDTH - 3):
            if grid[y][x] == grid[y + 1][x + 1] == grid[y + 2][x + 2] == grid[y + 3][x + 3] != " ":
                return grid[y][x]

    # vérifie les diagonales (bas-gauche vers haut-droite)
    for y in range(GRID_HEIGHT - 3):
        for x in range(GRID_WIDTH - 3):
            if grid[y + 3][x] == grid[y + 2][x + 1] == grid[y + 1][x + 2] == grid[y][x + 3] != " ":
                return grid[y + 3][x]

    # vérifie si la grille est pleine
    if all(all(token != " " for token in line) for line in grid):
        return "t"

    return ""


def game(player1: str, player2: str) -> None:
    """Lance une partie de puissance 4 et sauvegarde le score à la fin de la partie.

    Ce jeu utilise des séquences d'échappement ANSI pour afficher des couleurs des jetons.

    :param player1: Le nom du joueur 1 (celui qui commence)
    :param player2: Le nom du joueur 2
    """
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
            place_token(playing, P1_COLOR, grid)
        else:
            place_token(playing, P2_COLOR, grid)

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
        winner, loser = (player1, player2) if winner == make_token(P1_COLOR) else (player2, player1)
        add_score(winner, loser)

        display.screen(
            [f"{bold(winner)} a gagné !!!"],
            keys={"ENTER": "Continuer"},
        )

    while get_key() != "\n":
        pass
