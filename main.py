from parser import Parser
from simulation import Simulation
from pathfinder import Pathfinder
from sys import argv


def main() -> None:
    try:
        if len(argv) < 2:
            raise ValueError("Usage: python main.py <map_file>")
        parser = Parser(argv[1])
        parser.parse()
        if not parser.start_zone or not parser.end_zone:
            raise ValueError("start_zone or end_zone are not defined.")
        simulation = Simulation(
            zones=parser.zones,
            connections=parser.connections,
            drones=parser.drones,
            start_zone=parser.start_zone,
            end_zone=parser.end_zone
        )
        pathfinder = Pathfinder(parser.zones, parser.connections)
        paths_found = pathfinder.find_possible_paths(
            parser.start_zone,
            parser.end_zone,
            len(parser.drones)
        )
        paths = {}
        for drone in parser.drones:
            index = (drone.drone_id - 1) % len(paths_found)
            paths[drone] = paths_found[index]
        while not simulation.is_finished():
            simulation.run_turn(paths)
        for line in simulation.turn_log:
            print(line)
    except Exception as e:
        print(f"\033[31mError: {e}\033[0m")


if __name__ == "__main__":
    main()
