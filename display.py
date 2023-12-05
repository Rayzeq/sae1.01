from __future__ import annotations

import terminal
from terminal import get_key, green, red, strip_escapes


def print_at(x: int, y: int, text: str) -> None:
    """Écrit `text` en x,y sur le terminal.

    Le texte ne sera affiché qu'après avoir flush stdout.

    :param x:    La position x à laquelle écrire le texte (tout à gauche étant 1 et non 0)
    :param y:    La position y à laquelle écrire le texte (tout en haut étant 1 et non 0)
    :param text: Le texte à écrire
    """
    terminal.set_cursor(x, y)
    print(text, end="")


def display_at(text: list[str], x: int, y: int) -> None:
    """Écrit un bloc de texte sur plusieurs lignes avec le coin en haut à gauche en x,y.

    Le texte ne sera affiché qu'après avoir flush stdout.

    :param text: Les lignes de texte afficher
    :param x:    La position x à laquelle écrire le texte (tout à gauche étant 1 et non 0)
    :param y:    La position y à laquelle écrire le texte (tout en haut étant 1 et non 0)
    """
    line: str
    i: int

    for i, line in enumerate(text):
        print_at(x, y + i, line)


def hline(x: int, y1: int, y2: int, char: str) -> None:
    """Affiche une ligne horizontale composée de `char` entre `y1` et `y2` (les deux sont inclus).

    La ligne ne sera affiché qu'après avoir flush stdout.
    Si y1 > y2, rien ne sera affiché.

    :param x:    Le colonne où sera affiché la ligne (commence à 1 et non 0)
    :param y1:   La ligne où commencera la ligne (commence à 1 et non 0)
    :param y2:   La ligne où se finira la ligne (commence à 1 et non 0)
    :param char: Le caractère à utiliser
    """
    y: int

    for y in range(y1, y2 + 1):
        print_at(x, y, char)


def center(text_length: int, available_space: int) -> int:
    """Renvoie la position à laquelle il faut placer un texte de longueur `text_length`
    dans espace de `available_space` caractères pour qu'il soit centré.

    Attention à bien penser à supprimer les caractères non-imprimables (comme les séquences
    d'échappement ANSI) dans le calcule de la taille du texte.

    :param text_length:     La longueur du texte
    :param available_space: L'espace disponible
    :returns:               La position à laquelle doit être placé le texte
    """
    # do not factor this expression
    return available_space // 2 - text_length // 2


def main_frame() -> None:
    """Affiche le cadre principale du programme (un cadre en double ligne sur les bords du terminal).

    Le cadre ne sera affiché qu'après avoir flush stdout.
    """
    width: int
    height: int
    i: int

    width, height = terminal.get_size()

    print_at(1, 1, "╔" + "═" * (width - 2) + "╗")
    for i in range(2, height):
        print_at(1, i, "║")
        print_at(1 + width, i, "║")

    print_at(1, height + 1, "╚" + "═" * (width - 2) + "╝")


def keys_help(keys: dict[str, str]) -> None:
    """Affiche l'aide des touches en bas à gauche du terminal.

    L'aide ne sera affiché qu'après avoir flush stdout.

    :param keys: Un dictionnaire associant le nom des touches à leur action
    """
    i: int
    height: int
    name: str
    description: str

    _, height = terminal.get_size()
    for i, (name, description) in enumerate(keys.items()):
        print_at(3, height - len(keys) + i, f"{name}: {description}")


def screen(
    content: list[str],
    *,
    keys: dict[str, str] = {},
    decorations: list[tuple[int, int, str]] = [],
    center_all: bool = False,
) -> None:
    """Affiche un écran.

    Cette fonction:
      - efface tout ce qui est présent
      - affiche le cadre principal
      - affiche l'aide des touches
      - affiche les décorations
      - affiche le contenu principal
      - flush stdout, ce n'est donc pas nécessaire de le faire manuellement

    :param content:     Le contenu principal, sera centré en hauteur et en largeur
    :param keys:        Les touches pour lesquelles afficher l'aide (même format que pour `keys_help`)
    :param decorations: Les décorations à afficher, ce sont de simples textes avec leur position
    :param center_all:  Si `True` est passé, le contenu sera centré selon la longueur de toutes ses lignes,
                        sinon il sera centré selon la longueur de sa première ligne.
    """
    x: int
    y: int
    width: int
    height: int
    max_length: int
    text: str

    terminal.clear()
    main_frame()
    keys_help(keys)

    for x, y, text in decorations:
        print_at(x, y, text)

    if content:
        if center_all:
            max_length = max(len(strip_escapes(line)) for line in content)
        else:
            max_length = len(strip_escapes(content[0]))

        width, height = terminal.get_size()
        x = center(max_length, width)
        y = center(len(content), height)

        display_at(content, x, y)

    # force stdout to be flushed so everything we wrote is actually displayed
    print(end="", flush=True)


def prompt(question: str, *, decorations: list[tuple[int, int, str]] = [], invalid: list[str] = []) -> str:
    """Demande à l'utilisateur de rentrer un texte.

    :param question:    La question à afficher.
    :param decorations: Même chose que dans `screen`.
    :param invalid:     La liste des valeurs qui ne serons pas acceptées.
    :returns:           Le texte que l'utilisateur a entré.
    """
    key: str
    value: str = ""
    prompt: str

    terminal.show_cursor()

    while True:
        prompt = "\b\b"
        if value == "" or value in invalid:
            prompt += red("> ")
        else:
            prompt += green("> ")

        screen([question, prompt + value], keys={"ENTER": "Valider"}, decorations=decorations)

        key = get_key()

        if len(key) == 1 and key.isprintable() and key != "\t":
            value += key
        elif key == "BACKSPACE":
            value = value[:-1]
        elif key == "\n" and value != "" and value not in invalid:
            terminal.hide_cursor()
            return value


def check_number(number: int, minimum: int | None = None, maximum: int | None = None) -> bool:
    """Renvoie `True` si `number` est compris entre `minimum` et `maximum`.

    Si `minimum` est `None`, il n'y a pas minimum, et c'est la même chose pour `maximum`.

    :param number:  Le nombre à vérifier
    :param minimum: Le minimum, s'il y en a un
    :param maximum: Le maximum, s'il y en a un
    """
    if minimum is not None and number < minimum:
        return False
    if maximum is not None and number > maximum:
        return False
    return True


def prompt_int(
    question: str,
    minimum: int | None = None,
    maximum: int | None = None,
    *,
    decorations: list[tuple[int, int, str]] = [],
) -> int:
    """Demande à l'utilisateur de rentrer un nombre.

    Si le minimum n'est pas précisé, il n'y a pas de minimum (mais les nombres négatifs ne sont pas acceptés).
    Si le maximum n'est pas précisé, il n'y a pas de maximum.

    :param question:    La question à afficher.
    :param decorations: Même chose que dans `screen`.
    :returns:           Le nombre que l'utilisateur a entré.
    """
    key: str
    number: str = ""
    prompt: str
    keys: dict[str, str] = {"ENTER": "Valider"}

    terminal.show_cursor()

    while True:
        prompt = "\b\b"
        if number == "" or not check_number(int(number), minimum, maximum):
            prompt += red("> ")
        else:
            prompt += green("> ")
        prompt += number

        screen([question, prompt], keys=keys, decorations=decorations)

        key = get_key()

        if len(key) == 1 and key.isdigit():
            number += key
        elif key == "BACKSPACE":
            number = number[:-1]
        elif key == "\n" and number != "" and check_number(int(number), minimum, maximum):
            terminal.hide_cursor()
            return int(number)
