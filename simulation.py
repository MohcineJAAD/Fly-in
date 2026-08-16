from zone import Zone
from connection import Connection
from drone import Drone


class Simulation:
    """A class representing the simulation environment."""

    def __init__(
            self,
            zones: dict[str, Zone],
            connections: list[Connection],
            drones: list[Drone],
            start_zone: Zone,
            end_zone: Zone
    ) -> None:
        """Initialize the simulation from parsed map data.

        Args:
            zones: A dictionary of zones in the simulation.
            connections: All connections in the map.
            drones: All drones in the simulation.
            start_zone: The zone where drones start.
            end_zone: The zone where drones need to reach.
        """
        self.zones = zones
        self.connections = connections
        self.drones = drones
        self.start_zone = start_zone
        self.end_zone = end_zone
        self.turn_counter = 0
        self.turn_log: list[str] = []

    def is_finished(self) -> bool:
        """Check if all drones have reached the end zone.

        Returns:
            True if all drones reached the end zone
            False otherwise.
        """
        return all(drone.has_arrived(self.end_zone) for drone in self.drones)

    def get_active_drones(self) -> list[Drone]:
        """Get a list of drones that are not yet in the end zone.

        Returns:
            A list of drones still in transit.
        """
        return [
            drone for drone in self.drones
            if not drone.has_arrived(self.end_zone)
        ]
