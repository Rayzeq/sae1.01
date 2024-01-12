def get_display_name(name: str) -> str:
    """Récupère le nom d'affichage d'un joueur.

    Si le joueur est un humain, son nom est retourné.
    Si le joueur est un bot, "Bot 1" ou "Bot 2" est retourné.

    :param name: Le nom du joueur
    :returns:    Le nom d'affichage du joueur
    """
    if name[0] == "\t":
        return f"Bot {name[1]}"
    else:
        return name


def difficulty_level(name: str) -> int:
    """Récupère le niveau de difficulté du bot à partir de son nom.

    :param name: Le nom du bot
    :returns:    Le niveau de difficulté du bot (entre 0 et 3)
    """
    return int(name[2])
