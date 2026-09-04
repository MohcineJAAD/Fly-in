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

    def get_neighbors(
            self,
            zone: Zone,
            avoid: set[Connection] | None = None
    ) -> list[Zone]:
        """Get the neighboring zones of a given zone.

        Args:
            zone: The zone for which to find neighbors.
            avoid: A set of connections to avoid.

        Returns:
            A list of neighboring zones.
        """
        if avoid is None:
            avoid = set()
        neighbors = []
        for connection in self.connections:
            if connection in avoid:
                continue
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

    def find_path(
            self,
            start_zone: Zone,
            end_zone: Zone,
            avoid: set[Connection] | None = None
    ) -> list[Zone]:
        """Find a path between two zones

        Args:
            start_zone: The zone where the path starts.
            end_zone: The zone where the path ends.
            avoid: A set of connections to avoid.
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
            for neighbor in self.get_neighbors(current_zone, avoid):
                cost = self.get_zone_cost(neighbor)
                if cost is None:
                    continue
                new_cost = current_cost + cost
                if neighbor not in distances or new_cost < distances[neighbor]:
                    distances[neighbor] = new_cost
                    counter += 1
                    heapq.heappush(pq, (new_cost, counter, neighbor))
                    path[neighbor] = current_zone
        if end_zone not in path:
            return []
        route = [end_zone]
        while route[-1] != start_zone:
            route.append(path[route[-1]])
        route.reverse()
        return route

    def get_path_connections(self, path: list[Zone]) -> set[Connection]:
        """Get the connections used by the path.

        Args:
            path: A list of zones representing a route.

        Returns:
            The set of connections used to travel this path.
        """
        used_connections = set()
        for i in range(len(path) - 1):
            for connection in self.connections:
                if (connection.zone1 == path[i] and
                        connection.zone2 == path[i + 1]):
                    used_connections.add(connection)
                elif (connection.zone2 == path[i] and
                        connection.zone1 == path[i + 1]):
                    used_connections.add(connection)
        return used_connections

    def find_possible_paths(
                self,
                start_zone: Zone,
                end_zone: Zone,
                max_paths: int
    ) -> list[list[Zone]]:
        """Find multiple paths between two zones.

        Args:
            start_zone: The zone where the path starts.
            end_zone: The zone where the path ends.
            max_paths: The maximum number of paths to find.

        Returns:
            A list of paths, where each path is a list of zones.
        """
        first_path = self.find_path(start_zone, end_zone)
        if not first_path:
            raise ValueError(
                f"No valid path exists between '{start_zone.name}'"
                f" and '{end_zone.name}'."
            )
        paths = [first_path]
        cost = 0
        for zone in first_path[1:]:
            zone_cost = self.get_zone_cost(zone)
            if zone_cost is None:
                continue
            cost += zone_cost
        used_connections = self.get_path_connections(first_path)
        for connection in used_connections:
            candidate_path = self.find_path(
                start_zone, end_zone, avoid={connection}
            )
            if not candidate_path:
                continue
            if candidate_path in paths:
                continue
            candidate_cost = 0
            for zone in candidate_path[1:]:
                zone_cost = self.get_zone_cost(zone)
                if zone_cost is None:
                    continue
                candidate_cost += zone_cost
            if candidate_cost <= cost:
                paths.append(candidate_path)
        paths.sort(
            key=lambda path: any(
                zone.zone_type == ZoneType.PRIORITY for zone in path
            ),
            reverse=True
        )
        return paths


if __name__ == "__main__":
    from parser import Parser
    pf = Pathfinder({}, [])
    p = Parser("maps/easy/01_linear_path.txt")
    p.parse()
    for name in ["start", "waypoint1", "waypoint2", "goal"]:
        zone = p.zones[name]
        cost = pf.get_zone_cost(zone)
        print(f"{name}: ({zone.zone_type.value}): cost = {cost}")
