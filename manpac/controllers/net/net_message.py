from manpac.utils import export
from manpac.entity_type import EntityType
from manpac.direction import Direction
import manpac.controllers.net.net_boost_serializer as boost_serializer

from abc import ABC
import numpy as np


@export
def parse(message):
    if isinstance(message, str):
        s = message
    else:
        s = str(message, 'ascii')
    i = s.find(":")
    uid = int(s[:i])
    return _MESSAGES_[uid].from_string(s[i+1:])


class NetMessage(ABC):
    uid = 0
    compound = False

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "{}:".format(self.uid)

    @classmethod
    def from_string(cls, string):
        return cls()

    def bytes(self):
        return bytes(str(self), 'ascii')


@export
class MsgJoin(NetMessage):
    uid = 1

    def __init__(self, type):
        self.type = type

    def __str__(self):
        t = "g" if self.type is EntityType.GHOST else "p"
        return "{}:{}".format(self.uid, t)

    @classmethod
    def from_string(cls, string):
        if string[0] == "g":
            return MsgJoin(EntityType.GHOST)
        return MsgJoin(EntityType.PACMAN)


@export
class MsgResult(NetMessage):
    uid = 2

    def __init__(self, result):
        self.result = result

    def __str__(self):
        t = "t" if self.result else "f"
        return "{}:{}".format(self.uid, t)

    @classmethod
    def from_string(cls, string):
        return MsgResult(string[0] == "t")


@export
class MsgSyncMap(NetMessage):
    uid = 3

    def __init__(self, terrain):
        self.terrain = terrain

    def __str__(self):
        t = np.array2string(self.terrain, separator=",")
        return "{}:{}".format(self.uid, t)

    @classmethod
    def from_string(cls, string):
        rows = string.replace("[", "").replace("]", "").split("\n")
        width = len(rows)
        height = len(rows[0].split(","))
        terrain = np.zeros((width, height), dtype=np.int)
        for x, row in enumerate(rows):
            cols = row.split(",")[:-1] if row[-1] == "," else row.split(",")
            for y, el in enumerate(cols):
                terrain[x, y] = int(el)
        return MsgSyncMap(terrain)


@export
class MsgSyncEntity(NetMessage):
    uid = 4

    def __init__(self, **kwargs):
        if kwargs.get("entity", None) is not None:
            entity = kwargs["entity"]
            self.pos = entity.pos
            self.direction = entity.direction
            self.alive = entity.alive
            self.ent_uid = entity.uid
        else:
            self.pos = kwargs["pos"]
            self.direction = kwargs["direction"]
            self.alive = kwargs["alive"]
            self.ent_uid = kwargs["uid"]

    def __str__(self):
        t = np.array2string(self.pos, separator=",")
        end = "t" if self.alive else "f"
        return "{}:{}/{}/{}/{}".format(self.uid, t, self.direction.value, end, self.ent_uid)

    @classmethod
    def from_string(cls, string):
        parts = string.replace("[", "").replace("]", "").split("/")
        pos = np.array([float(x) for x in parts[0].strip().split(",")], dtype=np.float)
        direction = [d for d in Direction if d.value == int(parts[1])][0]
        return MsgSyncEntity(pos=pos, direction=direction, alive=parts[2] == "t", uid=int(parts[3]))


@export
class MsgSyncClock(NetMessage):
    uid = 5

    def __init__(self, ticks):
        self.ticks = ticks

    def __str__(self):
        return "{}:{}".format(self.uid, self.ticks)

    @classmethod
    def from_string(cls, string):
        return MsgSyncClock(float(string))


@export
class MsgCompound(NetMessage):
    uid = 6
    compound = True

    def __init__(self, *messages):
        self.messages = messages

    def __str__(self):
        s = "@".join([str(m) for m in self.messages])
        return "{}:{}".format(self.uid, s)

    @classmethod
    def from_string(cls, string):
        return MsgCompound(*[parse(s) for s in string.split("@")])


@export
class MsgSyncMapBoosts(NetMessage):
    uid = 7

    def __init__(self, ghost_boosts, pacman_boosts):
        self.pacman_boosts = pacman_boosts
        self.ghost_boosts = ghost_boosts

    def __str__(self):
        g = "@".join(["{},{},{}".format(loc[0], loc[1], duration) for (loc, duration) in self.ghost_boosts])
        p = "@".join(["{},{},{}".format(loc[0], loc[1], duration) for (loc, duration) in self.pacman_boosts])
        return "{}:{}u{}".format(self.uid, g, p)

    @classmethod
    def from_string(cls, string):
        boosts = string.split("u")
        ghosts = []
        for string in boosts[0].split("@"):
            data = string.split(",")
            if len(data) != 3:
                continue
            parsed = [np.array([int(data[0]), int(data[1])], dtype=np.int), float(data[2])]
            ghosts.append(parsed)
        pacmans = []
        for string in boosts[1].split("@"):
            data = string.split(",")
            if len(data) != 3:
                continue
            parsed = [np.array([int(data[0]), int(data[1])], dtype=np.int), float(data[2])]
            pacmans.append(parsed)
        return MsgSyncMapBoosts(ghosts, pacmans)


@export
class MsgEndGame(NetMessage):
    uid = 8


@export
class MsgBoostPickup(NetMessage):
    uid = 9

    def __init__(self, ent_uid, boost):
        self.ent_uid = ent_uid
        self.boost = boost
        self.boost_parsed = not isinstance(self.boost, str)

    def __str__(self):
        return "{}:{}/{}".format(self.uid, self.ent_uid, boost_serializer.serialize(self.boost))

    def parse_boost(self, game):
        if self.boost_parsed:
            return
        self.boost = boost_serializer.parse(self.boost, game)
        self.boost_parsed = True

    @classmethod
    def from_string(cls, string):
        data = string.split("/")
        return MsgBoostPickup(int(data[0]), data[1])


@export
class MsgYourEntity(NetMessage):
    uid = 10

    def __init__(self, ent_uid):
        self.ent_uid = ent_uid

    def __str__(self):
        return "{}:{}".format(self.uid, self.ent_uid)

    @classmethod
    def from_string(cls, string):
        return MsgYourEntity(int(string))


@export
class MsgStartGame(NetMessage):
    uid = 11


@export
class MsgBoostUse(NetMessage):
    uid = 12

    def __init__(self, ent_uid):
        self.ent_uid = ent_uid

    def __str__(self):
        return "{}:{}".format(self.uid, self.ent_uid)

    @classmethod
    def from_string(cls, string):
        return MsgBoostUse(int(string))


@export
class MsgSyncModifiers(NetMessage):
    uid = 13

    def __init__(self,  ent_uid, modifiers):
        self.ent_uid = ent_uid
        self.modifiers = modifiers
        self.boost_parsed = not self.modifiers or not isinstance(self.modifiers[0], str)

    def __str__(self):
        b = "@".join([boost_serializer.serialize(boost) for boost in self.modifiers])
        return "{}:{}/{}".format(self.uid, self.ent_uid, b)

    def parse_boost(self, game):
        if self.boost_parsed:
            return
        self.modifiers = [boost_serializer.parse(boost, game) for boost in self.modifiers]
        self.modifiers = [b for b in self.modifiers if b]
        self.boost_parsed = True

    @classmethod
    def from_string(cls, string):
        data = string.split("/")
        return MsgSyncModifiers(int(data[0]), data[1].split("@"))


_MESSAGES_ = {
    MsgJoin.uid: MsgJoin,
    MsgResult.uid: MsgResult,
    MsgSyncMap.uid: MsgSyncMap,
    MsgSyncEntity.uid: MsgSyncEntity,
    MsgSyncClock.uid: MsgSyncClock,
    MsgCompound.uid: MsgCompound,
    MsgSyncMapBoosts.uid: MsgSyncMapBoosts,
    MsgEndGame.uid: MsgEndGame,
    MsgBoostPickup.uid: MsgBoostPickup,
    MsgYourEntity.uid: MsgYourEntity,
    MsgStartGame.uid: MsgStartGame,
    MsgBoostUse.uid: MsgBoostUse,
    MsgSyncModifiers.uid: MsgSyncModifiers,
}
