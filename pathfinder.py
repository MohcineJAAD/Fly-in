import heapq
from zone import Zone, ZoneType
from connection import Connection


class Pathfinder:
    """Finds the lowest cost path between two zones in the map."""
    def __init__(
            self,
            zones: dict[str, Zone],
            connections: list[Connection]
    ) -> None:
        """Initialize the pathfinder with the necessary data.

        Args:
            zones: A dictionary of zones in the simulation.
            connections: all connections in the map.
        """
        self.zones = zones
        self.connections = connections

    def get_neighbors(self, zone: Zone) -> list[Zone]:
        """Get the neighboring zones of a given zone.

        Args:
            zone: The zone for which to find neighbors.

        Returns:
            A list of neighboring zones.
        """
        neighbors = []
        for connection in self.connections:
            if connection.zone1 == zone or connection.zone2 == zone:
                neighbors.append(connection.get_other_zone(zone))
        return neighbors

    def get_zone_cost(self, zone: Zone) -> int | None:
        """
        Get the cost of traversing a given zone.

        Args:
            zone: The zone for which to get the cost.

        Returns:
            The cost of traversing the zone, or None if the zone is blocked.
        """
        if zone.zone_type == ZoneType.BLOCKED:
            return None
        elif zone.zone_type == ZoneType.RESTRICTED:
            return 2
        return 1

    def find_path(self, start_zone: Zone, end_zone: Zone) -> list[Zone]:
        """Find a path between two zones

        Args:
            start_zone: The zone where the path starts.
            end_zone: The zone where the path ends.
        """
        distances = {start_zone: 0}
        counter = 0
        pq = [(0, counter, start_zone)]
        visited = set()
        path = {}
        while pq:
            current_cost, current_id, current_zone = heapq.heappop(pq)
            if current_zone in visited:
                continue
            if current_zone == end_zone:
                break
            visited.add(current_zone)
            for neighbor in self.get_neighbors(current_zone):
                cost = self.get_zone_cost(neighbor)
                if cost is None:
                    continue
                new_cost = current_cost + cost
                if neighbor not in distances or new_cost < distances[neighbor]:
                    distances[neighbor] = new_cost
                    counter += 1
                    heapq.heappush(pq, (new_cost, counter, neighbor))
                    path[neighbor] = current_zone

        route = [end_zone]
        while route[-1] != start_zone:
            route.append(path[route[-1]])
        route.reverse()
        return route


if __name__ == "__main__":
    from parser import Parser
    pf = Pathfinder({}, [])
    p = Parser("map.txt")
    p.parse()
    for name in ["start", "waypoint1", "waypoint3", "waypoint2", "goal"]:
        zone = p.zones[name]
        cost = pf.get_zone_cost(zone)
        print(f"{name}: ({zone.zone_type.value}): cost = {cost}")
