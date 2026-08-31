from parser import Parser
from simulation import Simulation
from pathfinder import Pathfinder


def main() -> None:
    parser = Parser("maps/easy/02_simple_fork.txt")
    parser.parse()
    if not parser.start_zone or not parser.end_zone:
        raise ValueError("start_zone and end_zone are not defined.")
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
        index = drone.drone_id % len(paths_found)
        paths[drone] = paths_found[index]
    while not simulation.is_finished():
        simulation.run_turn(paths)
    for line in simulation.turn_log:
        print(line)


if __name__ == "__main__":
    main()
