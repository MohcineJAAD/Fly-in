from zone import Zone
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

    def find_path(self, start_zone: Zone, end_zone: Zone) -> list[Zone]:
        """Find a path between two zones

        Args:
            start_zone: The zone where the path starts.
            end_zone: The zone where the path ends.
        """
        pass
