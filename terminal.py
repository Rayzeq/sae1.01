from __future__ import annotations

import os
import re
import sys
import termios
import tty
from typing import Any


def make_raw(fd: int) -> list[Any]:
    """Passe le terminal donné par `fd` en mode brute.

    Dans ce mode, le caractères entrés par l'utilisateur ne sont pas affichés sur le terminal
    et `read(1)` retourne au bout d'un seul charactère lu (n'attend pas un retour à la ligne).

    :param      fd:   Le file descriptor du terminal (généralement `sys.stdin.fileno()`)
    :type       fd:   int

    :returns:   Retourne le mode dans lequel était le terminal avant de passer en mode brute.
    :rtype:     Liste composée comme ça: [int, int, int, int, int, int, list[bytes | int]]
    """
    # this is from the signature of termios.tcgetattr
    original_mode: list[Any]
    # a better definition would be: tuple[int, int, int, int, int, int, list[bytes | int]]
    # but we can't use it because it's a list and not a tuple

    new_mode: list[Any]

    original_mode = termios.tcgetattr(fd)
    new_mode = original_mode.copy()
    new_mode[tty.CC] = original_mode[tty.CC].copy()

    new_mode[tty.LFLAG] &= ~(
        # do not echo characters written by the user
        termios.ECHO
        # disable canonical mode (allow the usage of VMIN)
        | termios.ICANON
    )

    new_mode[tty.CC][termios.VMIN] = 1
    new_mode[tty.CC][termios.VTIME] = 0

    termios.tcsetattr(fd, termios.TCSADRAIN, new_mode)
    return original_mode


def restore(fd: int, mode: list[Any]) -> None:
    """Restore le terminal donné par `fd` dans le mode `mode`.

    :param      fd:    Le file descriptor du terminal (généralement `sys.stdin.fileno()`)
    :type       fd:    int
    :param      mode:  Le mode dans lequel était le terminal était avant d'être passé en mode brute.
    :type       mode:  Liste composée comme ça: [int, int, int, int, int, int, list[bytes | int]]
    """
    termios.tcsetattr(fd, termios.TCSADRAIN, mode)


def hide_cursor() -> None:
    """Cache le curseur du terminal."""
    print("\x1b[?25l", end="")


def show_cursor() -> None:
    """Affiche le curseur du terminal."""
    print("\x1b[?25h", end="")


def get_size() -> tuple[int, int]:
    """Retourne la taille du terminal dans le format (largeur, hauteur).

    :returns:   La taille du terminal
    :rtype:     tuple[int, int]
    """
    return os.get_terminal_size()


def set_cursor(x: int, y: int) -> None:
    """Place le le curseur en x,y sur le terminal.

    :param      x:    La colonne où sera mis le curseur (la première colonne est 1 et non 0)
    :type       x:    int
    :param      y:    La ligne où sera mis le curseur (la première ligne est 1 et non 0)
    :type       y:    int
    """
    print(f"\x1b[{y};{x}H", end="")


def cursor_up(lines: int) -> None:
    """Déplace le curseur de `lines` lignes vers le haut, relativement à sa position actuelle.

    :param      lines:  Le nombre de lignes
    :type       lines:  int
    """
    print(f"\x1b[{lines}A", end="")


def cursor_left(columns: int) -> None:
    """Déplace le curseur de `columns` colonnes vers la gauche, relativement à sa position actuelle.

    :param      lines:  Le nombre de colonnes
    :type       lines:  int
    """
    print(f"\x1b[{columns}D", end="")


def clear() -> None:
    """Efface le terminal."""
    print("\x1b[2J", end="")


def red(text: str) -> str:
    """Retourne le text passé en entrée, avec les codes ANSI nécéssaires pour qu'il soit affiché en rouge.

    :param      text:  Le texte à colorer
    :type       text:  str

    :returns:   Le texte en couleur
    :rtype:     str
    """
    return f"\x1b[31m{text}\x1b[0m"


def green(text: str) -> str:
    """Retourne le text passé en entrée, avec les codes ANSI nécéssaires pour qu'il soit affiché en vert.

    :param      text:  Le texte à colorer
    :type       text:  str

    :returns:   Le texte en couleur
    :rtype:     str
    """
    return f"\x1b[32m{text}\x1b[0m"


def bold(text: str) -> str:
    """Retourne le text passé en entrée, avec les codes ANSI nécéssaires pour qu'il soit affiché en gras.

    :param      text:  Le texte à modifier
    :type       text:  str

    :returns:   Le texte en gras
    :rtype:     str
    """
    return f"\x1b[1m{text}\x1b[0m"


def invert(text: str) -> str:
    """Retourne le text passé en entrée, avec les codes ANSI nécéssaires pour qu'il soit affiché avec les couleurs de fond et de texte inversés.

    :param      text:  Le texte à modifier
    :type       text:  str

    :returns:   Le texte avec les couleurs inversées
    :rtype:     str
    """
    return f"\x1b[7m{text}\x1b[0m"


def get_key() -> str:
    r"""Lit un (et un seul) caractère depuis stdin.

    Les touches spéciales (qui commencent avec \x1b) lisent plusieurs caractères.
    Certaines touches spéciales sont reconnues et retourne leur nom. Ces touches sont
    UP, DOWN, RIGHT, LEFT qui représentent les flèches directionnelles et BACKSPACE qui représente la touche
    retour arrière.

    :returns:   Le caractère qui a été lu.
    :rtype:     str
    """
    next_char: str

    next_char = sys.stdin.read(1)
    if next_char == "\x1b":  # it's a special key
        sys.stdin.read(1)  # should be '['
        next_char = sys.stdin.read(1)

        if next_char == "A":  # up arrow
            next_char = "UP"
        elif next_char == "B":  # down arrow
            next_char = "DOWN"
        elif next_char == "C":  # right arrow
            next_char = "RIGHT"
        elif next_char == "D":  # left arrow
            next_char = "LEFT"
    elif next_char == "\x7f":
        next_char = "BACKSPACE"

    return next_char


def strip_escapes(text: str) -> str:
    # remove all the escape codes,  useful to get the real length of a string
    return re.sub(r"\x1b\[(\d+;?)+[a-zA-Z]", "", text)
