from zone import Zone, ZoneType
from connection import Connection
from drone import Drone


class Parser:
    """Reads a map file and builds zones, connections, and drones."""

    def __init__(self, file_path: str) -> None:
        """Create a parser for the given map file.

        Args:
            file_path: Path to the map file to read.
        """
        self.file_path = file_path
        self.zones: dict[str, Zone] = {}
        self.connections: list[Connection] = []
        self.drones: list[Drone] = []
        self.nb_drones = 0
        self.start_zone: Zone | None = None
        self.end_zone: Zone | None = None
        self.nb_drones_seen = False

    def parse_nb_drones(self, line: str) -> None:
        """Parse the number of drones from the first line of the map file.

        Args:
            line: The line containing the number of drones.

        Raises:
            ValueError: If the number of drones is not a positive integer
            or if the line format is incorrect.
        """

        try:
            self.nb_drones = int(line.strip(" ").split(":")[1])
            self.nb_drones_seen = True
        except (ValueError, IndexError):
            raise ValueError(
                "Invalid format of number of drones."
                " Expected format: 'Number of drones: <positive integer>'"
            )
        if self.nb_drones <= 0:
            raise ValueError("Number of drones must be a positive number.")

    def parse_zone_line(self, line: str) -> None:
        """Parse a zone line from the map file.

        Args:
            line: The line containing the zone information.

        Raises:
            ValueError: If the zone line format is incorrect or if coordinates
            are not integers.
            ValueError: If a duplicate zone name is found.
        """
        prefix, rest = line.split(":", 1)
        metadata = None
        if '[' in rest:
            before_bracket, metadata = rest.split("[", 1)
            if not metadata.rstrip().endswith(']'):
                raise ValueError(
                    "Metadata block is missing a closing bracket ']'."
                )
        else:
            before_bracket = rest
        try:
            name, x_str, y_str = before_bracket.split()
        except ValueError:
            raise ValueError(
                "Invalid zone format."
                " Expected format: '<zone_name> <x> <y> [metadata]'"
            )
        try:
            x = int(x_str)
            y = int(y_str)
        except ValueError:
            raise ValueError(
                f"Invalid coordinates for zone '{name}'."
                " Coordinates must be integers."
            )
        if name in self.zones:
            raise ValueError(f"Duplicate zone name: '{name}'.")
        if '-' in name:
            raise ValueError(
                f"Invalid zone name: '{name}':"
                " dashes are not allowed."
            )
        metadata_dict = {}
        if metadata:
            metadata = metadata.rstrip(']')
            pairs = metadata.split()
            for pair in pairs:
                try:
                    key, value = pair.split('=')
                except ValueError:
                    raise ValueError(
                        f"Invalid metadata format: '{pair}'."
                        " Expected format: 'key=value'"
                    )
                if key in metadata_dict:
                    raise ValueError(
                        f"Duplicate metadata key: '{key}'."
                    )
                metadata_dict[key] = value
            allowed_keys = {"zone", "color", "max_drones"}
            for key in metadata_dict:
                if key not in allowed_keys:
                    raise ValueError(f"Unknown metadata key: '{key}'.")
        try:
            max_drones = int(metadata_dict.get('max_drones', '1'))
        except ValueError:
            raise ValueError(
                "max_drones must be a valid integer."
            )
        if max_drones <= 0:
            raise ValueError(
                "max_drones must be a positive integer."
            )
        zone_type = ZoneType(metadata_dict.get('zone', 'normal'))
        color = metadata_dict.get('color', None)
        zone = Zone(name, x, y, zone_type, color, max_drones)
        self.zones[name] = zone
        if prefix.strip() == "start_hub":
            if zone_type == ZoneType.BLOCKED:
                raise ValueError(
                    f"'{name}' cannot be blocked: it is the start zone."
                )
            self.start_zone = zone
            zone.max_drones = self.nb_drones
        elif prefix.strip() == "end_hub":
            if zone_type == ZoneType.BLOCKED:
                raise ValueError(
                    f"{name}' cannot be blocked: it is the end zone."
                )
            self.end_zone = zone
            zone.max_drones = self.nb_drones

    def parse_connection_line(self, line: str) -> None:
        """Parse a connection line from the map file.

        Args:
            line: The line containing the connection information.

        Raises:
            ValueError: If the connection line format is incorrect or if it
            refers to undefined zones.
            ValueError: If a duplicate connection is found.
        """

        _, rest = line.split(":")
        metadata = None
        if '[' in rest:
            before_bracket, metadata = rest.split("[")
            if not metadata.rstrip().endswith(']'):
                raise ValueError(
                    "Metadata block is missing a closing bracket ']'."
                )
        else:
            before_bracket = rest
        try:
            zone1, zone2 = before_bracket.split("-")
        except ValueError:
            raise ValueError(
                "Invalid connection format."
                " Expected format: '<zone1>-<zone2> [metadata]'"
            )
        zone1 = zone1.strip()
        zone2 = zone2.strip()
        if zone1 == zone2:
            raise ValueError(
                f"Connection cannot link a zone to itself: '{zone1}'."
            )
        metadata_dict = {}
        if metadata:
            metadata = metadata.rstrip(']')
            pairs = metadata.split()
            for pair in pairs:
                try:
                    key, value = pair.split('=')
                except ValueError:
                    raise ValueError(
                        f"Invalid metadata format: '{pair}'."
                        " Expected format: 'key=value'"
                    )
                if key in metadata_dict:
                    raise ValueError(
                        f"Duplicate metadata key: '{key}'."
                    )
                metadata_dict[key] = value
            allowed_keys = {"max_link_capacity"}
            for key in metadata_dict:
                if key not in allowed_keys:
                    raise ValueError(f"Unknown metadata key: '{key}'.")
        try:
            max_link_capacity = int(
                metadata_dict.get('max_link_capacity', '1')
            )
        except ValueError:
            raise ValueError(
                "max_link_capacity must be a valid integer."
            )
        if max_link_capacity <= 0:
            raise ValueError(
                "max_link_capacity must be a positive integer."
            )
        zone1_obj = self.zones.get(zone1)
        zone2_obj = self.zones.get(zone2)
        if not zone1_obj or not zone2_obj:
            raise ValueError(
                "Connection refers to undefined zones: "
                f"'{zone1}' or '{zone2}'"
            )
        for connection in self.connections:
            if (
                (
                    connection.zone1 == zone1_obj and
                    connection.zone2 == zone2_obj
                )
                or
                (
                    connection.zone1 == zone2_obj and
                    connection.zone2 == zone1_obj
                )
            ):
                raise ValueError(
                    f"Duplicate connection: '{zone1}-{zone2}'."
                )
        connection = Connection(zone1_obj, zone2_obj, max_link_capacity)
        self.connections.append(connection)

    def build_drones(self) -> None:
        """Create drones and place them in the start zone.

        Raises:
            ValueError: If the start zone is not defined.
        """

        if self.start_zone is None:
            raise ValueError("Start zone is not defined.")
        for i in range(1, self.nb_drones + 1):
            drone = Drone(i, self.start_zone)
            self.drones.append(drone)
        self.start_zone.current_drones = self.nb_drones

    def parse(self) -> None:
        """Parse the map file and build zones, connections, and drones.

        Raises:
            ValueError: If any line in the file is malformed or invalid.
        """
        try:
            with open(self.file_path, 'r') as f:
                for line_nbr, line in enumerate(f, start=1):
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "#" in line:
                        line = line.split("#", 1)[0].strip()
                    try:
                        prefix = line.split(":", 1)[0].strip()
                        if prefix != "nb_drones" and not self.nb_drones_seen:
                            raise ValueError(
                                "The first line must define nb_drones."
                            )
                        if prefix == "nb_drones":
                            self.parse_nb_drones(line)
                        elif prefix in {"start_hub", "end_hub", "hub"}:
                            self.parse_zone_line(line)
                        elif prefix == "connection":
                            self.parse_connection_line(line)
                        else:
                            raise ValueError(
                                f"Unrecognized line format: '{line}'."
                            )
                    except ValueError as e:
                        raise ValueError(f"Line ({line_nbr}): {e}")
        except OSError:
            raise ValueError(f"Could not open map file: '{self.file_path}'")
        self.build_drones()
