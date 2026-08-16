from enum import Enum


class ZoneType(Enum):
    """The four allowed kinds of zones in the map."""

    NORMAL = "normal"
    RESTRICTED = "restricted"
    PRIORITY = "priority"
    BLOCKED = "blocked"


class Zone:
    """A single zone (node) in the drone map."""

    def __init__(
            self,
            name: str,
            x: int,
            y: int,
            zone_type: ZoneType = ZoneType.NORMAL,
            color: str | None = None,
            max_drones: int = 1
    ) -> None:
        """Create a zone.

        Args:
            name: The name of the zone.
            x: Integer x coordinate.
            y: Integer y coordinate.
            zone_type: Kind of zone. Default to NORMAL.
            color: Optional color of the zone. Default to None.
            max_drones: maximum simultaneous occupants. Default to 1.
        """
        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.color = color
        self.max_drones = max_drones
        self.current_drones = 0

    def has_space(self) -> bool:
        """Check if the zone has space for more drones.

        Returns:
            True if the zone has space for more drones, False otherwise.
        """
        return self.current_drones < self.max_drones

    def add_drone(self) -> None:
        """Add a drone to the zone if there is space.

        Raises:
            ValueError: If the zone has no available space.
        """
        if not self.has_space():
            raise ValueError(f"Zone '{self.name}' is full.")
        self.current_drones += 1

    def remove_drone(self) -> None:
        """Remove a drone from the zone.

        Raises:
            ValueError: If the zone has no drones to remove.
        """
        if self.current_drones == 0:
            raise ValueError(f"Zone '{self.name}' has no drones to remove.")
        self.current_drones -= 1
