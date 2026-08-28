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

    def can_move(self, drone: Drone, destination: Zone) -> bool:
        """Check if a drone can move into the destination zone.

        Args:
            drone: The drone attempting to move.
            destination: The zone the drone wants to move into.

        Returns:
            True if the destination has space, False otherwise.
        """
        return destination.has_space()

    def get_next_zone(self, drone: Drone, path: list[Zone]) -> Zone | None:
        """Get the next zone a drone should move to along its path.

        Args:
            drone: The drone whose next step we want to find.
            path: The full route the drone is following.

        Returns:
            The next zone to move to, or None if the drone has arrived.
        """
        index = path.index(drone.current_zone)
        if (index + 1) < len(path):
            return path[index + 1]
        return None

    def can_drone_move(self, drone: Drone, path: list[Zone]) -> bool:
        """Check whether a drone is able to move to its next zone.

        Args:
            drone: The drone to check.
            path: The path the drone is following.

        Returns:
            True if the drone can move to the next zone, False otherwise.
        """
        next_zone = self.get_next_zone(drone, path)
        if next_zone is None:
            return False
        if not self.can_move(drone, next_zone):
            return False
        return True

    def move_drone(self, drone: Drone, path: list[Zone]) -> bool:
        """Move a drone to its next zone along the path if possible.

        Args:
            drone: The drone to move.
            path: The path the drone is following.

        Returns:
            True if the drone was moved, False otherwise.
        """
        if not self.can_drone_move(drone, path):
            return False
        next_zone = self.get_next_zone(drone, path)
        if next_zone is None:
            return False
        drone.current_zone.remove_drone()
        drone.current_zone = next_zone
        next_zone.add_drone()
        return True

    def run_turn(self, paths: dict[Drone, list[Zone]]) -> None:
        """Run one simulation turn, moving all active drones

        Args:
            paths: Each drone's route from its current zone to the end zone.
        """
        turn_moves = []
        for drone in self.get_active_drones():
            path = paths[drone]
            if self.move_drone(drone, path):
                log = f"D{drone.drone_id}-{drone.current_zone.name}"
                turn_moves.append(log)
        if turn_moves:
            self.turn_log.append(" ".join(turn_moves))
        self.turn_counter += 1
