from zone import Zone, ZoneType
from connection import Connection
from drone import Drone


class Simulation:
    """A class representing the simulation environment."""

    COLORS = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "black": "\033[30m",
        "orange": "\033[38;5;208m",
        "purple": "\033[38;5;129m",
        "violet": "\033[38;5;135m",
        "brown": "\033[38;5;94m",
        "gold": "\033[38;5;220m",
        "lime": "\033[38;5;118m",
        "maroon": "\033[38;5;88m",
        "crimson": "\033[38;5;161m",
        "darkred": "\033[38;5;88m",
        "rainbow": "\033[38;5;201m",
        "reset": "\033[0m"
    }

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

    def get_connection(self, zone1: Zone, zone2: Zone) -> Connection:
        """Get the connection between two zones

        Args:
            zone1: The first zone.
            zone2: The second zone.

        Returns:
            The connection object linking the two zones.

        Raises:
            ValueError: If no connection exists between the two zones.
        """
        for connection in self.connections:
            if (
                (connection.zone1 == zone1 and connection.zone2 == zone2)
                or
                (connection.zone2 == zone1 and connection.zone1 == zone2)
            ):
                return connection
        raise ValueError("No connection found between the specified zones.")

    def can_move(self, drone: Drone, destination: Zone) -> bool:
        """Check if a drone can move into the destination zone.

        Args:
            drone: The drone attempting to move.
            destination: The zone the drone wants to move into.

        Returns:
            True if the destination has space, False otherwise.
        """
        connection = self.get_connection(drone.current_zone, destination)
        reserved_space = sum(
            1 for d in self.drones
            if d.target_zone == destination and d.turns_remaining > 0
        )
        effective_space = destination.max_drones
        effective_space -= (destination.current_drones + reserved_space)
        return effective_space > 0 and connection.has_space()

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

    def start_restricted_transit(
            self, drone: Drone,
            connection: Connection,
            destination: Zone
    ) -> None:
        """Start a drone transiting through a restrected connection.

        Args:
            drone: The drone to start transiting.
            connection: The connection the drone is transiting through.
            destination: The zone the drone is traveling to.
        """
        drone.current_zone.remove_drone()
        drone.current_connection = connection
        connection.add_drone()
        drone.target_zone = destination
        drone.turns_remaining = 1

    def finish_restricted_transit(self, drone: Drone) -> None:
        """Finish a drone transiting through a restricted connection.

        Args:
            drone: The drone to finish transiting.
        """
        if drone.current_connection is None or drone.target_zone is None:
            raise ValueError("Drone is not in restricted transit.")
        drone.turns_remaining -= 1
        drone.current_connection.remove_drone()
        drone.current_zone = drone.target_zone
        drone.target_zone.add_drone()
        drone.current_connection = None
        drone.target_zone = None

    def move_drone(self, drone: Drone, path: list[Zone]) -> bool:
        """Move a drone to its next zone along the path if possible.

        Args:
            drone: The drone to move.
            path: The path the drone is following.

        Returns:
            True if the drone was moved, False otherwise.
        """
        if drone.turns_remaining > 0:
            self.finish_restricted_transit(drone)
            return True
        if not self.can_drone_move(drone, path):
            return False
        next_zone = self.get_next_zone(drone, path)
        if next_zone is None:
            return False
        connection = self.get_connection(drone.current_zone, next_zone)
        if next_zone.zone_type == ZoneType.RESTRICTED:
            self.start_restricted_transit(drone, connection, next_zone)
            return True
        drone.current_zone.remove_drone()
        connection.add_drone()
        drone.current_zone = next_zone
        next_zone.add_drone()
        return True

    def run_turn(self, paths: dict[Drone, list[Zone]]) -> None:
        """Run one simulation turn, moving all active drones

        Args:
            paths: Each drone's route from its current zone to the end zone.
        """
        occupied_connections = set()
        for drone in self.drones:
            if (drone.turns_remaining > 0):
                occupied_connections.add(drone.current_connection)
        for connection in self.connections:
            if connection not in occupied_connections:
                connection.current_drones_in_transit = 0
        turn_moves = []
        for drone in self.get_active_drones():
            path = paths[drone]
            if self.move_drone(drone, path):
                prefix = f"D{drone.drone_id}-"
                reset = Simulation.COLORS["reset"]
                if (
                    drone.turns_remaining > 0 and
                    drone.current_connection is not None
                ):
                    zone1 = drone.current_connection.zone1
                    zone2 = drone.current_connection.zone2
                    color1 = Simulation.COLORS.get(zone1.color or "", "")
                    color2 = Simulation.COLORS.get(zone2.color or "", "")
                    zone_part = f"{color1}{zone1.name}{reset}"
                    zone_part += f"-{color2}{zone2.name}{reset}"
                else:
                    color = Simulation.COLORS.get(
                        drone.current_zone.color or "", ""
                    )
                    zone_part = f"{color}{drone.current_zone.name}{reset}"
                turn_moves.append(prefix + zone_part)
        if turn_moves:
            self.turn_log.append(" ".join(turn_moves))
        self.turn_counter += 1
