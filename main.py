from parser import Parser
from simulation import Simulation


def main() -> None:
    parser = Parser("map.txt")
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
    print(simulation.drones)

main()