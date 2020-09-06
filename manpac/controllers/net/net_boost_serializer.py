from manpac.utils import export
from manpac.modifiers.ghost_block_modifier import GhostBlockModifier
from manpac.modifiers.intangible_modifier import IntangibleModifier
from manpac.modifiers.speed_modifier import SpeedModifier
from manpac.modifiers.swap_modifier import SwapModifier


@export
def serialize(boost):
    if isinstance(boost, GhostBlockModifier):
        text = "gb{}".format(boost.remaining_duration)
    elif isinstance(boost, IntangibleModifier):
        text = "in{}".format(boost.remaining_duration)
    elif isinstance(boost, SpeedModifier):
        text = "sp{};{}".format(boost.remaining_duration, boost.speed_multiplier)
    elif isinstance(boost, SwapModifier):
        text = "sw{};{}".format(boost.range, boost.remaining_duration)
    return text


@export
def parse(text, game):
    identifier = text[:2]
    data = text[2:].split(";")
    if identifier == "gb":
        return GhostBlockModifier(game, float(data[0]))
    elif identifier == "in":
        return IntangibleModifier(game, float(data[0]))
    elif identifier == "sp":
        return SpeedModifier(game, float(data[0]), float(data[1]))
    elif identifier == "sw":
        return SwapModifier(game, float(data[0]), float(data[1]))
