"""Utilitaires pour contrôler le terminal.

La majorité des fonctions de ce module utilisent des codes d'échappement ANSI..
"""

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
    et `read(1)` retourne au bout d'un seul caractère lu (n'attend pas un retour à la ligne).

    :param fd: Le file descriptor du terminal (généralement `sys.stdin.fileno()`)

    :returns:  Retourne le mode dans lequel était le terminal avant de passer en mode brute.
    :rtype:    Liste composée comme ça: [int, int, int, int, int, int, list[bytes | int]]
    """
    # the type is from the signature of termios.tcgetattr
    original_mode: list[Any]

    new_mode: list[Any]

    original_mode = termios.tcgetattr(fd)
    # copy old attributes
    new_mode = original_mode.copy()
    new_mode[tty.CC] = original_mode[tty.CC].copy()

    new_mode[tty.LFLAG] &= ~(
        # do not echo characters written by the user
        termios.ECHO
        # disable canonical mode (allow the usage of VMIN)
        | termios.ICANON
    )

    # allow stdin.read(1) to return after reading only one character
    new_mode[tty.CC][termios.VMIN] = 1
    # see termios(3)
    new_mode[tty.CC][termios.VTIME] = 0

    termios.tcsetattr(fd, termios.TCSADRAIN, new_mode)
    return original_mode


def restore(fd: int, mode: list[Any]) -> None:
    """Restaure le terminal donné par `fd` dans le mode `mode`.

    :param fd:   Le file descriptor du terminal (généralement `sys.stdin.fileno()`)
    :param mode: Le mode dans lequel était le terminal était avant d'être passé en mode brute.
    :type  mode: Liste composée comme ça: [int, int, int, int, int, int, list[bytes | int]]
    """
    termios.tcsetattr(fd, termios.TCSADRAIN, mode)


def get_size() -> tuple[int, int]:
    """Retourne la taille du terminal dans le format (largeur, hauteur).

    :returns: La taille du terminal
    """
    return os.get_terminal_size()


def hide_cursor() -> None:
    """Cache le curseur du terminal.

    Cette fonction ne sera effective qu'après avoir flush stdout.
    """
    print("\x1b[?25l", end="")


def show_cursor() -> None:
    """Affiche le curseur du terminal.

    Cette fonction ne sera effective qu'après avoir flush stdout.
    """
    print("\x1b[?25h", end="")


def set_cursor(x: int, y: int) -> None:
    """Place le curseur en x,y sur le terminal.

    Cette fonction ne sera effective qu'après avoir flush stdout.
    Si l'une des deux coordonnées est négative, rien ne se passera.
    Si les coordonnées sont en dehors de l'écran, le curseur sera "clamp" sur les bords.

    :param x:    La colonne où sera mis le curseur (la première colonne est 1 et non 0)
    :param y:    La ligne où sera mis le curseur (la première ligne est 1 et non 0)
    """
    print(f"\x1b[{y};{x}H", end="")


def set_cursor_x(x: int) -> None:
    """Place le curseur à la colonne `x` sur le terminal.

    Cette fonction ne sera effective qu'après avoir flush stdout.
    Si x est négative, rien ne se passera.
    Si x est en dehors de l'écran, le curseur sera "clamp" sur les bords.

    :param x:    La colonne où sera mis le curseur (la première colonne est 1 et non 0)
    """
    print(f"\x1b[{x}G", end="")


def cursor_up(lines: int) -> None:
    """Déplace le curseur de `lines` lignes vers le haut, relativement à sa position actuelle.

    Cette fonction ne sera effective qu'après avoir flush stdout.

    :param lines:  Le nombre de lignes
    """
    print(f"\x1b[{lines}A", end="")


def cursor_left(columns: int) -> None:
    """Déplace le curseur de `columns` colonnes vers la gauche, relativement à sa position actuelle.

    Cette fonction ne sera effective qu'après avoir flush stdout.

    :param      lines:  Le nombre de colonnes
    """
    print(f"\x1b[{columns}D", end="")


def clear() -> None:
    """Efface le terminal.

    Cette fonction ne sera effective qu'après avoir flush stdout.
    """
    print("\x1b[2J", end="")


def red(text: str) -> str:
    """Retourne le texte passé en entrée, avec les codes ANSI nécessaires pour qu'il soit affiché en rouge.

    :param text: Le texte à colorer
    :returns:     Le texte en couleur
    """
    return f"\x1b[31m{text}\x1b[0m"


def green(text: str) -> str:
    """Retourne le texte passé en entrée, avec les codes ANSI nécessaires pour qu'il soit affiché en vert.

    :param text: Le texte à colorer
    :returns:    Le texte en couleur
    """
    return f"\x1b[32m{text}\x1b[0m"


def gray(text: str) -> str:
    """Retourne le texte passé en entrée, avec les codes ANSI nécessaires pour qu'il soit affiché en vert.

    :param text: Le texte à colorer
    :returns:    Le texte en couleur
    """
    return f"\x1b[90m{text}\x1b[0m"


def bold(text: str) -> str:
    """Retourne le texte passé en entrée, avec les codes ANSI nécessaires pour qu'il soit affiché en gras.

    :param text: Le texte à modifier
    :returns:    Le texte en gras
    """
    return f"\x1b[1m{text}\x1b[0m"


def invert(text: str) -> str:
    """Retourne le texte passé en entrée, avec les codes ANSI nécessaires pour qu'il soit affiché avec les couleurs
    de fond et de texte inversés.

    :param text: Le texte à modifier
    :returns:    Le texte avec les couleurs inversées
    """
    return f"\x1b[7m{text}\x1b[0m"


def get_key() -> str:
    r"""Lit un (et un seul) caractère depuis stdin.

    Les touches spéciales (qui commencent avec \x1b) lisent plusieurs caractères.
    Certaines touches spéciales sont reconnues et retourne leur nom. Ces touches sont UP, DOWN, RIGHT, LEFT qui
    représentent les flèches directionnelles et BACKSPACE qui représente la touche retour arrière.

    :returns: Le caractère qui a été lu.
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
    """Supprime les escape codes ANSI qui commencent avec un CSI et retourne le résultat.

    Très utile pour trouver la "vrai longueur" d'une chaîne (le nombre de caractères qui sont visibles).

    :param text: Le texte à nettoyer
    :returns:    Le texte sans les escapes codes ANSI
    """
    return re.sub(r"\x1b\[(\d+;?)+[a-zA-Z]", "", text)
