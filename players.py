def get_display_name(name: str) -> str:
    if name[0] == "\t":
        return f"Bot {name[1]}"
    else:
        return name


def difficulty_level(name: str) -> int:
    return int(name[2])
