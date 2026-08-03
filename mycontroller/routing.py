from collections import deque

from pox.core import core

log = core.getLogger()


class RoutingManager(object):

    def __init__(
        self,
        topology
    ):

        self.topology = topology

    def shortest_path(
        self,
        src,
        dst
    ):

        if src == dst:
            return [src]

        queue = deque()

        queue.append(src)

        visited = {
            src
        }

        parent = {}

        while queue:

            current = queue.popleft()

            for neighbor in self.topology.neighbors(current):

                if neighbor in visited:
                    continue

                visited.add(
                    neighbor
                )

                parent[neighbor] = current

                if neighbor == dst:

                    path = [dst]

                    while path[-1] != src:

                        path.append(
                            parent[path[-1]]
                        )

                    path.reverse()

                    return path

                queue.append(
                    neighbor
                )

        return None