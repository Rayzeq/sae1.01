from __future__ import annotations

import random
from random import randint

import display
import terminal
from display import center, waiting_screen
from players import difficulty_level, get_display_name
from scores import get_scores, set_scores
from terminal import bold, get_key

SCOREBOARD = "allumettes"
RULES = [
    "Dans ce jeu, l'objectif est de ne pas être le dernier à prendre une allumette.",
    "Le gagnant est celui qui fait que l'autre prenne la dernière allumette disponible.",
    "A tour de rôle, chaque joueur pourra prendre entre 1 et 3 allumettes comprises.",
    "Ce jeu se joue normalement avec 20 allumettes, mais vous pouvez en choisir un peu plus ou un peu moins.",
]


def add_score(winner: str, loser: str) -> None:
    """Met à jour le score des deux joueurs dans la base de donnée des scores.

    Le gagnant se voit ajouter une victoire et les deux joueurs se voient ajouter une partie jouée.

    :param winner: Le nom du gagnant
    :param loser:  Le nom du perdant
    """
    scores: dict[str, list[float]]

    scores = dict(get_scores(SCOREBOARD))
    if winner[0] != "\t" and winner not in scores:
        scores[winner] = [0, 0]
    if loser[0] != "\t" and loser not in scores:
        scores[loser] = [0, 0]

    if winner[0] != "\t":
        scores[winner][0] += 1
        scores[winner][1] += 1
    if loser[0] != "\t":
        scores[loser][1] += 1

    set_scores(SCOREBOARD, scores.items())


def get_sorted_scores() -> list[tuple[str, str]]:
    """Retourne les scores triés par ordre décroissant (un score plus grand est meilleur).

    Le score d'un joueur représente son pourcentage de victoires.

    :returns: Les scores triés.
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


def auto_choose(bot_name: str, matches_count: int) -> int:
    """Choisis un nombre d'allumettes à prendre en fonction du niveau de difficulté du bot.

    Si cette fonction est appelée avec le nom d'un joueur, son comportement n'est pas définie.

    :param bot_name:      Le nom du bot (qui contient des métadonnées sur sa difficultée)
    :param matches_count: Le nombre d'allumettes restante
    :returns:             Le nombre d'allumettes à prendre
    """
    diff_level = difficulty_level(bot_name)

    if diff_level == 1:  # niveau de difficulté moyen
        # le bot à 1 chance sur 2 de faire le meilleur choix
        diff_level = random.choice((0, 2))

    if diff_level == 0:  # niveau de difficulté facile
        return randint(1, 3)
    else:  # niveau de difficulté difficile
        if matches_count % 4 == 0:
            to_take = 3
        else:
            target = (matches_count // 4) * 4 + 1
            to_take = matches_count - target
        if (to_take <= 0) or (to_take > 3):
            # ce code sera exécuté si le bot se retrouve avec un nombre d'allumettes avec lequel il ne peut pas gagner
            return 1
        else:
            return to_take


def game(player1: str, player2: str) -> None:
    """Lance une partie du jeu des allumettes et sauvegarde le score à la fin de la partie.

    :param player1: Le nom du joueur 1 (celui qui commence)
    :param player2: Le nom du joueur 2
    """
    matches: int
    playing: str
    waiting: str
    matches_display: list[tuple[int, int, str]]
    width: int
    height: int
    y: int
    choice: int

    if player1[0] == player2[0] == "\t":
        matches = randint(15, 30)
        waiting_screen(f"La partie commencera avec {bold(str(matches))} allumettes")
    else:
        matches = display.prompt_int(
            f"Avec quel nombre d'allumettes la partie va commencer (entre {bold(str(15))} et {bold(str(30))}) ?",
            15,
            30,
        )

    playing, waiting = player2, player1
    while matches > 0:
        playing, waiting = waiting, playing

        width, height = terminal.get_size()
        y = height // 4 - 6 // 2

        matches_display = [
            (center(2 * matches, width), y + 0, "▆ " * matches),
            (center(2 * matches, width), y + 1, "┃ " * matches),
            (center(2 * matches, width), y + 2, "┃ " * matches),
            (center(2 * matches, width), y + 3, "┃ " * matches),
            (center(2 * matches, width), y + 4, "┃ " * matches),
            (center(2 * matches, width), y + 5, "┃ " * matches),
        ]

        if playing[0] == "\t":
            choice = auto_choose(playing, matches)
            waiting_screen(f"{bold(get_display_name(playing))} enlève {bold(str(choice))} allumettes", matches_display)
            matches -= choice
        else:
            matches -= display.prompt_int(
                f"{bold(get_display_name(playing))}, combien voulez-vous prendre d'allumettes (entre {bold(str(1))} et {bold(str(3))}) ?",
                1,
                3,
                decorations=matches_display,
            )

    add_score(waiting, playing)

    display.screen(
        [f"{bold(get_display_name(waiting))} a gagné !!!"],
        keys={"ENTER": "Continuer"},
    )

    while get_key() != "\n":
        pass
