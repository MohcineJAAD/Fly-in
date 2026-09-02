from zone import Zone
from connection import Connection


class Drone:
    """A class representing a drone in the simulation."""

    def __init__(self, drone_id: int, start_zone: Zone) -> None:
        """Create a new drone with a unique identifier.

        Args:
            drone_id: Unique identifier for the drone.
            start_zone: The zone where the drone starts.
        """
        self.drone_id = drone_id
        self.current_zone = start_zone
        self.current_connection: Connection | None = None
        self.target_zone: Zone | None = None
        self.turns_remaining = 0

    def has_arrived(self, end_zone: Zone) -> bool:
        """Check if the drone has arrived at the specified end zone.

        Args:
            end_zone: The zone to check.

        Returns:
            True if the drone is in the end zone, False otherwise.
        """
        return self.current_zone == end_zone
