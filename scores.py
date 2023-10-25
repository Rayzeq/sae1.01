from __future__ import annotations

from pathlib import Path
from typing import Iterable, TypeAlias

SCORES_PATH = Path(__file__).parent.resolve() / "scores"
ScoreLine: TypeAlias = tuple[str, list[float]]


def get_scores(game: str) -> list[ScoreLine]:
    lines: list[str]
    scores: list[ScoreLine] = []
    path: Path
    name: str
    numbers: list[str]

    SCORES_PATH.mkdir(parents=True, exist_ok=True)
    path = SCORES_PATH.joinpath(game.lower() + ".txt")
    path.touch(exist_ok=True)

    with path.open() as f:
        lines = f.readlines()

    for line in lines:
        name, *numbers = line.rsplit("\t")
        scores.append((name, list(map(float, numbers))))

    return scores


def set_scores(game: str, scores: Iterable[ScoreLine]) -> None:
    path: Path
    name: str
    numbers: list[float]
    numbers_str: str

    SCORES_PATH.mkdir(parents=True, exist_ok=True)
    path = SCORES_PATH.joinpath(game.lower() + ".txt")
    path.touch(exist_ok=True)

    with path.open("w") as f:
        for name, numbers in scores:
            numbers_str = "\t".join(map(str, numbers))
            f.write(f"{name}\t{numbers_str}\n")
