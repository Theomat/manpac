from manpac.utils import export
from manpac.direction import Direction
from queue import PriorityQueue


import numpy as np


@export
class PathGraph():
    """
    Represent a graph of the map which allows for easy path finding.

    Parameters
    -----------
    - *map*: (**Map**)
        the map this graph will represent
    """

    def __init__(self, map):
        self.map = map
        self.nodes = np.zeros_like(map.terrain) - 1
        self.nodes_data = []
        self.buffer = np.zeros_like(self.nodes, dtype=np.bool)
        self.debug = False
        self._build_()

    def _is_node_candidate_(self, pos):
        if not self.map.is_walkable(pos):
            return False
        for d in Direction:
            around = [d for d in Direction if self.map.is_walkable(pos + d.vector)]
            if len(around) == 1:
                return True
            for d1 in around:
                for d2 in around:
                    if np.sum(np.abs(d1.vector * d2.vector)) == 0:
                        return True
        return False

    def _find_first_node_(self):
        pos = np.zeros((2), dtype=np.int)
        for x in range(self.map.width):
            pos[0] = x
            for y in range(self.map.height):
                pos[1] = y
                if not self._is_node_candidate_(pos):
                    continue
                return pos

    def _add_node_(self, pos):
        if self.nodes[pos[0], pos[1]] < 0:
            numero = len(self.nodes_data)
            self.nodes[pos[0], pos[1]] = numero
            self.nodes_data.append({'pos': pos.copy()})
            if self.debug:
                self.map[pos] = 2
            return True
        return False

    def _link_(self, src, dst, direction, distance):
        isrc = self.nodes[src[0], src[1]]
        idst = self.nodes[dst[0], dst[1]]
        self.nodes_data[isrc][direction] = [dst, distance]
        self.nodes_data[idst][-direction] = [src, distance]

    def _build_(self):
        # Find one node
        first_node = self._find_first_node_()
        self._add_node_(first_node)

        # Exploration
        self.buffer[:, :] = False
        nodes = [first_node]
        while nodes:
            origin = nodes.pop(0)
            if self.buffer[origin[0], origin[1]]:
                continue
            self.buffer[origin[0], origin[1]] = True
            for d in Direction:
                if not self.map.is_walkable(origin + d.vector):
                    continue
                current = origin.copy()
                current += d.vector
                dist = 1
                while not self._is_node_candidate_(current):
                    current += d.vector
                    dist += 1
                self._add_node_(current)
                self._link_(origin, current, d, dist)
                nodes.append(current)

    def closest_nodes(self, pos):
        """
        Find the closest reachable nodes to the specified position.
        Parameters
        -----------
        - *pos*: (**numpy.ndarray**)
            the source position
        Return
        -----------
        The list of the closest reachable nodes surrounding the position.
        type: **List[numpy.ndarray]**
        """
        map_pos = np.floor(pos).astype(dtype=np.int)
        # If current pos is node then return it
        if self.nodes[map_pos[0], map_pos[1]] >= 0:
            return [map_pos]
        # Otherwise find the closest
        nodes = []
        for direction in Direction:
            current = map_pos + direction.vector
            while self.map.is_walkable(current) and not (self.nodes[current[0], current[1]] >= 0):
                current += direction.vector
            if self.map.is_walkable(current):
                nodes.append(current)
        return nodes

    def path(self, src, dst):
        """
        Find a list of walkable tiles from src to dst.
        Only returns the tiles where a direction change is needed.

        Parameters
        -----------
        - *src*: (**numpy.ndarray**)
            the source position
        - *dst*: (**numpy.ndarray**)
            the destination position, it must be walkable

        Return
        -----------
        A list of tiles that needs to be reached where a direction change occurs if a path exists and the distance.
        type: **Tuple[List[numpy.ndarray], float]**
        """
        src_nodes = self.closest_nodes(src)
        dst_nodes = self.closest_nodes(dst)
        best = []
        best_distance = 1e12
        for src_node in src_nodes:
            for dst_node in dst_nodes:
                path, distance = self.node_path(src_node, dst_node)
                distance += np.sum(np.abs(src_node - src))
                distance += np.sum(np.abs(dst_node - dst))
                if distance < best_distance:
                    best = path
                    best_distance = distance
        best.append(dst)
        return best, best_distance

    def node_path(self, src_node, dst_node):
        """
        Find a list of walkable tiles from src to dst.
        Only returns the tiles where a direction change is needed.

        Parameters
        -----------
        - *src*: (**numpy.ndarray**)
            the source position, must be a node
        - *dst*: (**numpy.ndarray**)
            the destination position, must be a node

        Return
        -----------
        A list of tiles that needs to be reached where a direction change occurs if a path exists and the distance.
        type: **Tuple[List[numpy.ndarray], float]**
        """
        max_d = np.sum(np.abs(dst_node - src_node))
        if max_d == 0:
            return [src_node, dst_node], 0
        self.buffer[:, :] = False
        paths = PriorityQueue()
        path_num = 1
        # (distance traveled, last_position)
        paths.put([0, 0, src_node, [src_node]])
        while not paths.empty():
            distance, p, pos, path = paths.get()
            ipos = self.nodes[pos[0], pos[1]]
            node_data = self.nodes_data[ipos]
            for direction in Direction:
                dst_info = node_data.get(direction, None)
                if dst_info is None:
                    continue
                new_pos, added_distance = dst_info
                if self.buffer[new_pos[0], new_pos[1]]:
                    continue
                self.buffer[new_pos[0], new_pos[1]] = True
                new_distance = distance + added_distance
                if (new_pos == dst_node).all():
                    path.append(dst_node)
                    return path, new_distance
                new_path = path[:]
                new_path.append(new_pos)
                paths.put([new_distance, path_num, new_pos, new_path])
                path_num += 1
        return [], 1e12
