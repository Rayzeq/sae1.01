from __future__ import annotations

import terminal
from terminal import get_key, green, red, strip_escapes


def print_at(x: int, y: int, text: str) -> None:
    terminal.set_cursor(x, y)
    print(text, end="")


def display_at(text: list[str], x: int, y: int) -> None:
    line: str
    i: int

    for i, line in enumerate(text):
        print_at(x, y + i, line)


def hline(x: int, y1: int, y2: int, char: str) -> None:
    for y in range(y1, y2 + 1):
        print_at(x, y, char)


def center(text_length: int, available_space: int) -> int:
    # do not factor this expression
    return available_space // 2 - text_length // 2


def main_frame() -> None:
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
    x: int
    y: int
    width: int
    height: int
    max_length: int
    line: str

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

        for i, line in enumerate(content):
            print_at(x, y + i, line)

    # force stdout to be flushed so everything we wrote is actually displayed
    print(end="", flush=True)


def prompt(question: str, *, decorations: list[tuple[int, int, str]] = []) -> str:
    key: str
    value: str = ""
    prompt: str

    terminal.show_cursor()

    while True:
        prompt = "\b\b"
        if value == "":
            prompt += red("> ")
        else:
            prompt += green("> ")

        screen([question, prompt + value], keys={"ENTER": "Valider"}, decorations=decorations)

        key = get_key()

        if len(key) == 1 and key.isprintable():
            value += key
        elif key == "BACKSPACE":
            value = value[:-1]
        elif key == "\n" and value != "":
            terminal.hide_cursor()
            return value


def check_number(number: int, minimum: int | None = None, maximum: int | None = None) -> bool:
    if minimum is not None and number < minimum:
        return False
    if maximum is not None and number > maximum:
        return False
    return True


def prompt_int(
    message: str,
    minimum: int | None = None,
    maximum: int | None = None,
    *,
    decorations: list[tuple[int, int, str]] = [],
) -> int:
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

        screen([message, prompt], keys=keys, decorations=decorations)

        key = get_key()

        if len(key) == 1 and key.isdigit():
            number += key
        elif key == "BACKSPACE":
            number = number[:-1]
        elif key == "\n" and number != "" and check_number(int(number), minimum, maximum):
            terminal.hide_cursor()
            return int(number)
