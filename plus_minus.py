from __future__ import annotations

import display
import terminal
from scores import ScoreLine, get_scores, set_scores
from terminal import bold, get_key, green, red

SCOREBOARD = "plus_minus"


def prompt_int(message: str, decorations: list[tuple[int, int, str]] = [], hidable: bool = False) -> int:
    key: str
    number: str = ""
    prompt: str
    hidden: bool = False
    keys: dict[str, str] = {"ENTER": "Valider"}

    if hidable:
        keys["H"] = "Cache le nombre"
        keys["S"] = "Affiche le nombre"

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
    scores: list[ScoreLine]
    score: float

    score = round(guess_count / maximum * 100, 3)

    scores = get_scores(SCOREBOARD)
    scores.append((player, [score]))

    set_scores(SCOREBOARD, scores)


def get_sorted_scores() -> list[tuple[str, str]]:
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
    max: int
    number: int
    guess: int = -1
    guess_count: int = 0
    answer: str
    p1_lives: int = 2
    decorations: list[tuple[int, int, str]] = []

    max = display.prompt_int(f"{bold(player1)} choisit la borne maximum (minimum 10)", 10)
    decorations.append((3, 2, f"Maximum: {max}"))

    number = prompt_int(f"{bold(player1)} choisit un nombre", decorations, hidable=True)
    while number > max:
        number = prompt_int("Votre nombre ne peut pas dépasser le nombre maximum", decorations, hidable=True)

    decorations.append((3, 3, f"Nombre d'essais: {bold(str(guess_count))}"))
    decorations.append((3, 4, f"Vie(s) de {bold(player1)}: {bold(str(p1_lives))}"))

    while (guess != number) and (p1_lives > 0):
        guess_count += 1
        guess = prompt_int(f"{bold(player2)} devine", decorations)

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
