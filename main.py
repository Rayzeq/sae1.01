#!/usr/bin/env nix-shell
#!nix-shell -i python3 -p python3

from __future__ import annotations

import sys
from typing import Any

import allumettes
import display
import morpion
import plus_minus
import terminal
from display import center, display_at, print_at
from terminal import bold, get_key, green, invert

TITLE = [
    "   _______  _________  _____  ____  ___  ___  ___  ____",
    "  / __/ _ \\/  _/ __/ |/ / _ \\/ __/ |_  |/ _ \\|_  ||_  /",
    " / _// , _// // _//    / // /\\ \\  / __// // / __/_/_ < ",
    "/_/ /_/|_/___/___/_/|_/____/___/ /____/\\___/____/____/ ",
]


def display_scoreboard(x: int, y: int, width: int, height: int, name: str) -> None:
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
    else:
        print("TODO")
        scores = []

    for i, (name, score) in zip(range(y + 1, y + height), scores):
        score_width = width - 3 - len(name)
        print_at(x + 1, i, f" {name}{score:>{score_width}} ")

    if len(scores) > height - 1:
        print_at(x + 1, y + height - 1, invert(green("TODO".center(width - 1))))


def display_all_scoreboards(x: int, width: int, height: int, scoreboards: list[str]) -> None:
    main_title: str = "TABLEAUX DES SCORES"
    remaining_space: int
    scoreboard_height: int
    last_scoreboard_height: int
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
    display.keys_help({"↑ / ↓": "Choisir une option", "ENTER": "Valider"})

    display_all_scoreboards(width - 40, 40, height, ["PLUS OU MOINS", "ALLUME-LE", "MORPION", "PUISSANCE 4"])

    x = center(max_width, width)
    y = center(len(options), height)

    for i, line in enumerate(options):
        if i == selected:
            print_at(x - 2, y + i, green("> ") + invert(line.center(max_width)) + green(" <"))
        else:
            print_at(x, y + i, line.center(max_width))
    print(end="", flush=True)


def main_menu(options: list[str]) -> int:
    selected: int = 0
    key: str

    while True:
        terminal.clear()
        display_main_menu(options, selected)

        key = get_key()
        if key == "UP":
            selected = max(selected - 1, 0)
        elif key == "DOWN":
            selected = min(selected + 1, len(options) - 1)
        elif key == "\n":
            return selected


def login_screen(player: str) -> str:
    return display.prompt(f"NOM DU {bold(player)}")


def get_player_roles(question: str, player1: str, player2: str) -> tuple[str, str]:
    p1: str
    p2: str
    key: str
    content: list[str]

    p1, p2 = player1, player2
    content = [bold(question), "", ""]

    while True:
        content[1] = p1
        content[2] = p2

        if player1 == p1:
            content[1] = "\b\b" + green("> ") + invert(p1)
        if player1 == p2:
            content[2] = "\b\b" + green("> ") + invert(p2)

        display.screen(content, keys={"ENTER": "Valider"})

        key = get_key()
        if key in ("UP", "DOWN"):
            player1, player2 = player2, player1
        elif key == "\n":
            return player1, player2


def real_main() -> None:
    player1: str
    player2: str
    role1: str
    role2: str
    selection: int

    player1 = login_screen("JOUEUR 1")
    player2 = login_screen("JOUEUR 2")

    while True:
        selection = main_menu(["PLUS OU MOINS", "ALLUME-LE", "MORPION", "PUISSANCE 4", "QUITTER"])
        match selection:
            case 0:
                role1, role2 = get_player_roles("Qui fera deviner à l'autre ?", player1, player2)
                plus_minus.game(role1, role2)
            case 1:
                role1, role2 = get_player_roles("Qui commence ?", player1, player2)
                allumettes.game(role1, role2)
            case 2:
                role1, role2 = get_player_roles("Qui commence ?", player1, player2)
                morpion.game(role1, role2)
            case 3:
                pass
            case 4:
                break


def main() -> None:
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
