from manpac.utils import export
from manpac.entity_type import EntityType
from manpac.direction import Direction

from abc import ABC, abstractmethod
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

    @classmethod
    @abstractmethod
    def from_string(cls, string):
        pass

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
class MsgDoTick(NetMessage):
    uid = 5

    def __init__(self, ticks):
        self.ticks = ticks

    def __str__(self):
        return "{}:{}".format(self.uid, self.ticks)

    @classmethod
    def from_string(cls, string):
        return MsgDoTick(float(string))


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


_MESSAGES_ = {
    MsgJoin.uid: MsgJoin,
    MsgResult.uid: MsgResult,
    MsgSyncMap.uid: MsgSyncMap,
    MsgSyncEntity.uid: MsgSyncEntity,
    MsgDoTick.uid: MsgDoTick,
    MsgCompound.uid: MsgCompound,
}
