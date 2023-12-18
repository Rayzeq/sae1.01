#!/usr/bin/env nix-shell
#!nix-shell -i python3 -p python3

from __future__ import annotations

import sys
from typing import Any

import allumettes
import display
import morpion
import plus_minus
import pow4
import terminal
from display import center, display_at, print_at
from terminal import bold, get_key, gray, green, invert, strip_escapes

SCOREBOARD_WIDTH = 40
TITLE = [
    "   _______  _________  _____  ____  ___  ___  ___  ____",
    "  / __/ _ \\/  _/ __/ |/ / _ \\/ __/ |_  |/ _ \\|_  ||_  /",
    " / _// , _// // _//    / // /\\ \\  / __// // / __/_/_ < ",
    "/_/ /_/|_/___/___/_/|_/____/___/ /____/\\___/____/____/ ",
]


def display_scoreboard(x: int, y: int, width: int, height: int, name: str) -> None:
    """Affiche le tableau des scores pour un jeu.

    :param x:      La colonne à laquelle le tableau des scores sera affiché
    :param y:      La ligne à laquelle le tableau des scores sera affiché
    :param width:  La largeur attribuée au tableau des scores
    :param height: La hauteur attribuée au tableau des scores
    :param name:   Le nom du jeu pour lequel le tableau des scores doit être affiché
    """
    scores: list[tuple[str, str]]
    i: int
    score: str
    score_width: int

    print_at(x + center(len(name), width), y, bold(name))

    if name == "PLUS OU MOINS":
        scores = plus_minus.get_sorted_scores()
    elif name == "ALLUME-LE":
        scores = allumettes.get_sorted_scores()
    elif name == "MORPION":
        scores = morpion.get_sorted_scores()
    elif name == "PUISSANCE 4":
        scores = pow4.get_sorted_scores()
    else:
        scores = [("jeu invalide!!!", "-1")]

    for i, (name, score) in zip(range(y + 1, y + height), scores):
        if len(name) > width - 10:
            name = name[: width - 11] + gray("…")

        score_width = width - 3 - len(strip_escapes(name))
        print_at(x + 1, i, f" {name}{score:>{score_width}} ")

    if len(scores) > height - 1:
        print_at(x + 1, y + height - 1, gray("…".center(width - 1)))


def display_all_scoreboards(x: int, width: int, height: int, scoreboards: list[str]) -> None:
    """Affiche tout les tableaux des scores.

    :param x:           La colonne à laquelle seront placés les tableaux des scores
    :param width:       La largeur attribuée aux tableaux des scores
    :param height:      La hauteur attribuée aux tableaux des scores
    :param scoreboards: Les noms des jeux pour lesquels le tableau des scores doit être affiché
    """
    main_title: str = "TABLEAUX DES SCORES"
    remaining_space: int
    scoreboard_height: int
    last_scoreboard_height: int
    scoreboard: str
    y: int

    print_at(x, 1, "╦")
    display.hline(x, 2, height - 1, "║")
    print_at(x, height + 1, "╩")

    print_at(x + center(len(main_title), width), 2, bold(main_title))
    print_at(x, 3, "╠" + "═" * (width - 1) + "╣")

    remaining_space = height - 4 - len(scoreboards) - 1
    scoreboard_height = remaining_space // len(scoreboards)
    last_scoreboard_height = scoreboard_height + remaining_space % len(scoreboards)

    y = 4
    for scoreboard in scoreboards[:-1]:
        display_scoreboard(x, y, width, scoreboard_height, scoreboard)
        print_at(x, y + scoreboard_height, "╠" + "═" * (width - 1) + "╣")
        y += scoreboard_height + 1
    display_scoreboard(x, y, width, last_scoreboard_height, scoreboards[-1])


def display_main_menu(options: list[str], selected: int) -> None:
    """Affiche le menu principal (avec les tableaux des scores).

    :param options:  Les options du menu principal
    :param selected: L'indice de l'option qui est actuellement sélectionnée
    """
    max_width: int
    width: int
    height: int
    x: int
    y: int
    i: int
    line: str

    max_width = max(len(option) for option in options) + 2

    terminal.clear()
    width, height = terminal.get_size()

    display.main_frame()
    display_at(TITLE, center(len(TITLE[0]), width), 8)
    display.keys_help({"q": "Quitter", "↑ / ↓": "Choisir une option", "ENTER": "Valider"})

    display_all_scoreboards(
        width - SCOREBOARD_WIDTH,
        SCOREBOARD_WIDTH,
        height,
        ["PLUS OU MOINS", "ALLUME-LE", "MORPION", "PUISSANCE 4"],
    )

    x = center(max_width, width)
    y = center(len(options), height)

    for i, line in enumerate(options):
        if i == selected:
            print_at(x - 2, y + i, green("> ") + invert(line.center(max_width)) + green(" <"))
        else:
            print_at(x, y + i, line.center(max_width))
    print(end="", flush=True)


def main_menu(options: list[str]) -> int:
    """Affiche le menu principal et gère les entrées de l'utilisateur.

    :param options: Les options du menu principale
    :returns:       L'option que l'utilisateur à choisit. C'est un indice dans la liste `options`, ou -1 si l'utilisateur à quitté.
    """
    selected: int = 0
    key: str

    while True:
        terminal.clear()
        display_main_menu(options, selected)

        key = get_key()
        if key == "UP":
            selected = (selected - 1) % len(options)
        elif key == "DOWN":
            selected = (selected + 1) % len(options)
        elif key == "q":
            return -1
        elif key == "\n":
            return selected


def login_screen(player: str, player1: str | None = None) -> str:
    """Demande à un joueur d'entrer son nom.

    :param player:  Le joueur pour lequel on demande le nom (e.g "Joueur 1")
    :param player1: Si précisé, le nom du joueur 1. Ce nom ne pourra pas être réutilisé
    :returns:       Le nom que le joueur à choisis
    """
    if player1 is None:
        return display.prompt_player(f"NOM DU {bold(player)}", invalid=[])
    else:
        return display.prompt_player(f"NOM DU {bold(player)}", invalid=[player1])


def get_display_name(name: str) -> str:
    if name.startswith("\t"):
        return f"Bot {name[1]}"
    else:
        return name


def get_player_roles(question: str, player1: str, player2: str, rules: list[str]) -> tuple[str, str]:
    """Obtient les rôles des joueurs.

    :param question: La question a afficher (quel rôle est en train d'être choisi)
    :param player1:  Le nom du joueur 1 (l'ordre n'a pas d'importance)
    :param player2:  Le nom du joueur 2
    :param rules:    Les règles du jeu pour lequel un rôle est en train d'être choisi

    :returns:   Le joueur qui à été selectionné en premier et l'autre en deuxième. Si l'utilisateur est revenu au menu principal ("", "") sera retourné.
    """
    p1: str
    p2: str
    content: list[str]
    width: int
    height: int
    y: int
    i: int
    line: str
    key: str

    p1, p2 = player1, player2
    content = [bold(question), "", ""]

    while True:
        content[1] = get_display_name(p1)
        content[2] = get_display_name(p2)

        if player1 == p1:
            content[1] = "\b\b" + green("> ") + invert(content[1])
        if player1 == p2:
            content[2] = "\b\b" + green("> ") + invert(content[2])

        display.screen(content, keys={"q": "Écran titre", "ENTER": "Valider"})

        width, height = terminal.get_size()
        y = center(len(rules), height // 2)

        for i, line in enumerate(rules):
            print_at(center(len(line), width), y + i, line)

        print("", end="", flush=True)

        key = get_key()
        if key in ("UP", "DOWN"):
            player1, player2 = player2, player1
        elif key == "q":
            return ("", "")
        elif key == "\n":
            return player1, player2


def real_main() -> None:
    """Demande aux joueurs d'entrer leurs noms puis affiche le menu principal.

    Pour chaque jeu cette fonction demandera aussi le rôle de chaque joueur.
    """
    player1: str
    player2: str
    role1: str
    role2: str
    selection: int

    player1 = login_screen("JOUEUR 1")
    player2 = login_screen("JOUEUR 2", player1)

    while True:
        selection = main_menu(["PLUS OU MOINS", "ALLUME-LE", "MORPION", "PUISSANCE 4", "QUITTER"])
        if selection == 0:
            role1, role2 = get_player_roles("Qui fera deviner à l'autre ?", player1, player2, plus_minus.RULES)
            if role1 == "":
                continue
            plus_minus.game(role1, role2)
        elif selection == 1:
            role1, role2 = get_player_roles("Qui commence ?", player1, player2, allumettes.RULES)
            if role1 == "":
                continue
            allumettes.game(role1, role2)
        elif selection == 2:
            role1, role2 = get_player_roles("Qui commence ?", player1, player2, morpion.RULES)
            if role1 == "":
                continue
            morpion.game(role1, role2)
        elif selection == 3:
            role1, role2 = get_player_roles("Qui commence ?", player1, player2, pow4.RULES)
            if role1 == "":
                continue
            pow4.game(role1, role2)
        elif selection in (-1, 4):
            break


def main() -> None:
    """Cette fonction passe le terminal en mode "raw" et appelle `real_main`, puis repasse le terminal en mode normal avant la fin du programme."""
    screen: int
    mode: list[Any]

    screen = sys.stdin.fileno()
    mode = terminal.make_raw(screen)

    # the try-except is here to make sure that the terminal
    # don't stay in "raw" mode when our program exits, even
    # if it crashes
    try:
        real_main()
    finally:
        terminal.set_cursor(0, 0)
        terminal.show_cursor()
        terminal.clear()
        terminal.restore(screen, mode)


if __name__ == "__main__":
    main()
