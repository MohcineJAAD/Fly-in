from zone import Zone


class Connection:
    """A connection between two zones."""

    def __init__(
            self,
            zone1: Zone,
            zone2: Zone,
            max_link_capacity: int = 1
    ) -> None:
        """Create a connection between two zones.

        Args:
            zone1: One endpoint of the connection.
            zone2: The other endpoint of the connection.
            max_link_capacity: Maximum drones that can traverse this
                connection simultaneously. Default to 1.
        """
        self.zone1 = zone1
        self.zone2 = zone2
        self.max_link_capacity = max_link_capacity
        self.current_drones_in_transit = 0

    def has_space(self) -> bool:
        """Check if the connection has space for more drones.

        Returns:
            True if the connection has space for more drones, False otherwise.
        """
        return self.current_drones_in_transit < self.max_link_capacity

    def add_drone(self) -> None:
        """Add a drone to the connection if there is space.

        Raises:
            ValueError: If the connection has no available space.
        """
        if not self.has_space():
            raise ValueError(
                f"Connection between '{self.zone1.name}'"
                f" and '{self.zone2.name}' is full."
            )
        self.current_drones_in_transit += 1

    def remove_drone(self) -> None:
        """Remove a drone from the connection.

        Raises:
            ValueError: If the connection has no drones to remove.
        """
        if self.current_drones_in_transit == 0:
            raise ValueError(
                f"Connection between '{self.zone1.name}'"
                f" and '{self.zone2.name}' has no drones to remove."
            )
        self.current_drones_in_transit -= 1

    def get_other_zone(self, from_zone: Zone) -> Zone:
        """Get the zone on the other end of the conection.

        Args:
            from_zone: The zone from which the drone is coming.

        Returns:
            The zone on the other end of the connection.

        Raises:
            ValueError: If from_zone is not part of the connection.
        """

        if from_zone == self.zone1:
            return self.zone2
        if from_zone == self.zone2:
            return self.zone1
        raise ValueError(
            f"Zone '{from_zone.name}' is not part of this connection."
        )
