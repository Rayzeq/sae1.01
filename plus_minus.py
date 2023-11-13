from __future__ import annotations

import display
import terminal
from scores import ScoreLine, get_scores, set_scores
from terminal import bold, get_key, green, red

SCOREBOARD = "plus_minus"
RULES = [
    "Le but du jeu pour le deuxième joueur est de deviner le nombre choisis par le premier joueur.",
    "Le premier joueur choisi une limite maximale, et le nombre que le deuxième devra chercher et trouver.",
    "Le deuxième joueur propose des nombres et le premier indique si son nombre est supérieur, égal, ou inférieur.",
    "Le premier joueur possède deux vie où il peut se tromper dans ses réponses (la vraie réponse sera affichée).",
    "Si le premier joueur perd toutes ses vies le jeu s'arrête et le deuxième joueur gagne",
]


def prompt_int_hideable(message: str, decorations: list[tuple[int, int, str]] = []) -> int:
    """Demande à l'utilisateur de rentrer un nombre qui peut être caché si nécessaire.

    :param message:     Le message à afficher
    :param decorations: Même chose que pour `display.screen`
    :param hidable:     Vrai si la valeur entrée par l'utilisateur peut être cachée
    :returns:           Le nombre entré par l'utilisateur
    """
    key: str
    number: str = ""
    prompt: str
    hidden: bool = False
    keys: dict[str, str] = {"ENTER": "Valider", "H": "Cacher le nombre", "S": "Afficher le nombre"}

    terminal.show_cursor()

    while True:
        prompt = "\b\b"
        if number == "":
            prompt += red("> ")
        else:
            prompt += green("> ")

        if hidden:
            prompt += "<invisible>"
        else:
            prompt += number

        display.screen([message, prompt], keys=keys, decorations=decorations)

        key = get_key()

        if len(key) == 1 and key.isdigit():
            number += key
        elif key == "BACKSPACE":
            number = number[:-1]
        elif key.lower() == "h":
            hidden = True
        elif key.lower() == "s":
            hidden = False
        elif key == "\n" and number != "":
            terminal.hide_cursor()
            return int(number)


def prompt_plus_minus(player1: str, player2: str, guess: int, decorations: list[tuple[int, int, str]] = []) -> str:
    """Demande au joueur qui fait deviner si son nombre est plus grand, plus petit, ou égal au nombre proposé.

    :param player1:     Le joueur qui fait deviner
    :param player2:     Le joueur qui devine
    :param guess:       Le nombre proposé par `player2`
    :param decorations: Même chose que pour `display.screen`
    :returns:           La réponse du joueur, représenté par "+", "-" ou "="
    """
    question: str
    msg_greater: str = "  + si ton nombre est plus grand"
    msg_lower: str = "  - si ton nombre est plus petit"
    msg_equal: str = "  = si c'est ton nombre"
    key: str = ""

    question = f"{bold(player2)} a choisit {bold(str(guess))}, {bold(player1)}, tape sur:"

    display.screen([question, msg_greater, msg_lower, msg_equal], decorations=decorations)

    while key not in ("+", "-", "="):
        key = get_key()

    return key


def add_score(player: str, guess_count: int, maximum: int) -> None:
    """Ajoute le score du joueur qui vient de deviner.

    Le score dépends du nombre d'essais et de la borne maximum du nombre à deviner.

    :param player:      Le nom du joueur qui a deviné
    :param guess_count: Le nombre d'essais dont le joueur a eu besoin
    :param maximum:     La borne maximum du nombre à deviner
    """
    scores: list[ScoreLine]
    score: float

    score = round(guess_count / maximum * 100, 3)

    scores = get_scores(SCOREBOARD)
    scores.append((player, [score]))

    set_scores(SCOREBOARD, scores)


def get_sorted_scores() -> list[tuple[str, str]]:
    """Retourne les scores triés par ordre croissant (un score plus petit est meilleur).

    :returns: Les scores triés.
    :rtype:   Une liste de tuples (nom du joueur, score).
    """
    score_lines: list[ScoreLine]
    player: str
    score: float
    scores: list[tuple[str, str]] = []

    score_lines = get_scores(SCOREBOARD)
    score_lines.sort(key=lambda x: x[1][0])

    for player, (score,) in score_lines:
        scores.append((player, f"{score:.3f}"))

    return scores


def game(player1: str, player2: str) -> None:
    """Lance une partie de plus ou moins et sauvegarde le score à la fin de la partie.

    :param player1: Le nom du joueur 1 (celui qui choisi le chiffre)
    :param player2: Le nom du joueur 2 (celui qui devine)
    """
    max: int
    number: int
    guess: int = -1
    guess_count: int = 0
    answer: str
    p1_lives: int = 2
    decorations: list[tuple[int, int, str]] = []

    max = display.prompt_int(f"{bold(player1)} choisit la borne maximum (minimum 10)", 10)
    decorations.append((3, 2, f"Maximum: {max}"))

    number = prompt_int_hideable(f"{bold(player1)} choisit un nombre", decorations)
    while number > max:
        number = prompt_int_hideable("Votre nombre ne peut pas dépasser le nombre maximum", decorations)

    decorations.append((3, 3, f"Nombre d'essais: {bold(str(guess_count))}"))
    decorations.append((3, 4, f"Vie(s) de {bold(player1)}: {bold(str(p1_lives))}"))

    while (guess != number) and (p1_lives > 0):
        guess_count += 1
        guess = display.prompt_int(f"{bold(player2)} devine", decorations=decorations)

        decorations[1] = (3, 3, f"Nombre d'essais: {bold(str(guess_count))}")

        answer = prompt_plus_minus(player1, player2, guess, decorations)
        if (
            (number > guess and answer != "+")
            or (number < guess and answer != "-")
            or (number == guess and answer != "=")
        ):
            p1_lives -= 1

        decorations[2] = (3, 4, f"Vie(s) de {bold(player1)}: {bold(str(p1_lives))}")

        if p1_lives == 0:
            display.screen(
                [f"{bold(player1)} s'est trompé deux fois, {bold(player2)} gagne !"],
                keys={"ENTER": "Écran titre"},
                decorations=decorations,
            )
        elif number > guess:
            display.screen(
                [f"Le nombre est plus grand que {bold(str(guess))} !"],
                keys={"ENTER": "Continuer"},
                decorations=decorations,
            )
        elif number < guess:
            display.screen(
                [f"Le nombre est plus petit que {bold(str(guess))} !"],
                keys={"ENTER": "Continuer"},
                decorations=decorations,
            )
        else:
            display.screen(
                [f"Bravo ! {bold(player2)} a trouvé en {bold(str(guess_count))} essais"],
                keys={"ENTER": "Continuer"},
                decorations=decorations,
            )

        while get_key() != "\n":
            pass

    add_score(player2, guess_count, max)
