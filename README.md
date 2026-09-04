*This project has been created as part of the 42 curriculum by mjaad.*

# Fly-in

## Description

Fly-in is a drone routing simulator. It parses a map file describing zones
(hubs) and connections between them, computes efficient routes using a
hand-implemented Dijkstra's algorithm, and simulates multiple drones moving
simultaneously from a start zone to an end zone while respecting zone
capacity, connection capacity, restricted-zone transit times, and
priority-zone preferences.

The project is fully object-oriented, uses no external graph libraries, and
is type-checked with `mypy` and linted with `flake8`.

## Instructions

### Requirements

- Python 3.10+
- `pip` (or another package manager)

### Installation

```
make install
```

Installs `flake8` and `mypy` from `requirements.txt`.

### Running the simulation

```
make run MAP=path/to/your/map.txt
```

Or directly:

```
python3 main.py path/to/your/map.txt
```

If `MAP` is omitted, `make run` uses a default sample map.

### Other Makefile targets

- `make debug` — runs the simulation through Python's built-in debugger (`pdb`)
- `make clean` — removes `__pycache__` and `.mypy_cache`
- `make lint` — runs `flake8` and `mypy` with the required flags
- `make lint-strict` — runs `flake8` and `mypy --strict`

## Resources

- [Red Blob Games — Introduction to A\*](https://www.redblobgames.com/pathfinding/a-star/introduction.html) — visual, interactive explanation of Dijkstra and A*, used to understand the relationship between the two algorithms and decide between them.
- [Wikipedia — Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm) — used to confirm the correctness conditions (non-negative edge weights) and the proof sketch behind the algorithm's guarantee.
- [Python official docs — `heapq`](https://docs.python.org/3/library/heapq.html) — used as the priority queue for Dijkstra; confirmed the standard tie-breaking pattern (pushing `(cost, counter, item)` tuples) recommended for items that aren't natively comparable.
- [GeeksforGeeks — Dijkstra's Shortest Path Algorithm](https://www.geeksforgeeks.org/dsa/dijkstras-shortest-path-algorithm-greedy-algo-7/) — used as a reference implementation to compare against while debugging.

### AI usage

Claude (Anthropic) was used throughout this project as a tutor, not as a
code generator. The typical workflow was: Claude explained a concept or
pattern (e.g. the config-vs-state split, exceptions vs. boolean returns,
`mypy`'s Optional-narrowing rules, Dijkstra's mechanics), and I wrote every
line of code myself. Claude was also used to:

- Review code I had already written and point out real bugs (e.g. a loose
  `or` condition in a zone-matching check, a missing `connection.add_drone()`
  call that silently broke connection-capacity tracking, a per-turn reset
  that conflicted with multi-turn restricted transit, a capacity check
  that only counted arrived drones and not drones already en route).
- Run my code against constructed test maps to verify claims empirically
  rather than by assertion, and to help me design test maps that isolated
  a specific rule (e.g. a map with a genuine cost tie between a priority
  route and a non-priority route, or a map where a blocked zone made the
  goal completely unreachable).
- Systematically stress-test the parser against malformed input I
  proposed (duplicate zone names, dashes in names, unbalanced metadata
  brackets, duplicate metadata keys, unknown metadata keys, self-loop
  connections, lines with valid-looking but incorrect prefixes, files
  that don't exist, files with the wrong first line) so that each gap
  found was fixed with a clear, line-numbered error message instead of a
  raw Python traceback.
- Discuss trade-offs given time constraints (e.g. deciding not to build a
  full exit-before-entry fairness rule after empirically testing that it
  did not trigger through the normal simulation pipeline).

No code was copy-pasted from AI output without being typed and understood
by hand first.

## Algorithm Choices and Implementation Strategy

### Graph representation

Zones and connections are represented entirely with hand-written classes
(`Zone`, `Connection`) — no graph library is used, per the subject's
constraints. `Connection` objects store direct references to their two
`Zone` objects, so the graph is a plain object graph rather than an
adjacency list/matrix.

### Pathfinding

Shortest paths are computed with a hand-implemented Dijkstra's algorithm
(`Pathfinder.find_path`), using Python's `heapq` as the priority queue,
with a `(cost, counter, zone)` tuple to break ties safely without needing
`Zone` objects to be directly comparable. Dijkstra was chosen over BFS
(which assumes uniform edge cost — incorrect here, since `restricted`
zones cost 2 turns) and over A* (which would add a heuristic-design risk
for a negligible speed benefit at this project's map sizes). Since all
zone costs are non-negative (1 or 2), Dijkstra is guaranteed correct. If
no path exists between the start and end zone (for example, because a
`blocked` zone sits on the only possible route), `find_path` returns an
empty list, and `find_possible_paths` raises a clear error rather than
letting the problem surface later as a confusing crash.

`restricted` zones cost 2 turns, `normal` and `priority` zones cost 1
turn. `priority` zones do not cost less than `normal` zones — the spec's
"preferred" language is implemented as a tie-break: when multiple routes
tie on total cost, `Pathfinder.find_possible_paths` sorts any
priority-zone-containing route to the front of the result list.

### Multi-path distribution

`Pathfinder.find_possible_paths` finds the cheapest route, then tries
temporarily blocking each connection that route used (one at a time),
re-running Dijkstra to see if a genuinely different, equal-or-cheaper
route exists. Discovered routes are deduplicated and returned as a list.
Drones are then assigned to routes round-robin
(`(drone_id - 1) % number_of_routes`), so multiple equally-good routes
get used in parallel instead of every drone bottlenecking on a single
path.

### Turn-based simulation

Each turn, every active drone attempts one move. `Simulation.can_move`
checks both destination zone capacity and connection capacity before
allowing a move. Zone capacity is checked using an "effective space"
calculation that also accounts for drones already **en route** to a zone
(started transit but not yet arrived) — not just drones already present —
to correctly reject moves that would otherwise cause a capacity overflow
on arrival.

### Restricted-zone transit

Restricted zones take 2 turns to enter. A drone starting this transit is
removed from its current zone and tracked via `Drone.current_connection`,
`Drone.target_zone`, and `Drone.turns_remaining`, rather than moving
instantly. The output log correctly switches to printing the connection
name (`D<id>-<zone1>-<zone2>`) while a drone is mid-transit, and back to
the zone name once it arrives, matching the required output format.
Connection capacity for a connection currently used by an in-progress
restricted transit is not reset at the start of the following turn, so
the capacity limit is respected across the full duration of the crossing.

### Parser hardening

Beyond the happy path, the parser explicitly rejects: duplicate zone
names, dashes or spaces in zone names, non-positive or non-numeric
capacity values, malformed or unbalanced metadata blocks (`key=value`
pairs with missing `=`, unclosed `[...]`), duplicate or unrecognized
metadata keys, connections referring to undefined zones, duplicate
connections (`a-b` and `b-a` are treated as the same connection),
self-loop connections, a `start_hub` or `end_hub` marked as `blocked`,
lines with an unrecognized or malformed prefix, a first line that isn't
`nb_drones`, and a missing or unreadable map file. Every error raised
during parsing includes the line number it occurred on. Inline comments
(text following a `#` partway through an otherwise valid line) are
stripped rather than rejected.

### Known limitation

An "exit-before-entry" fairness edge case was identified and tested: if a
drone attempts to enter a zone in the same turn another drone is leaving
it, and the entering drone is checked before the leaving drone in that
turn's processing order, the entering drone can be delayed by one turn
even though the move should be valid. This was deliberately tested against
the actual simulation pipeline (not just in isolation): because drones are
always processed in a consistent order each turn, and that consistent
order tends to favor the drone that arrived at a bottleneck first (which
also tends to be the one leaving first), this situation was difficult to
trigger through normal multi-path, multi-drone simulation runs. Given this
low observed practical risk and time constraints, a full two-phase
move-resolution system was not implemented. The simulation is not at risk
of crashing or producing invalid state from this — at worst, a move is
delayed by a single unnecessary turn.

## Visual Representation

The simulation prints colored terminal output. Each zone's `color`
metadata (from the map file) is used to color that zone's name in the
turn log, using ANSI escape codes. During restricted-zone transit, both
zone names in the connection label (`D1-hub-roof1`) are colored
independently, using each zone's own color, rather than a single shared
color for the whole line. This makes it easy to visually track which type
of zone each drone is currently occupying or crossing, turn by turn.

## Example

Given a map file with a fork between two equally-cheap paths:

```
nb_drones: 4

start_hub: start 0 0 [color=green]
hub: junction 1 0 [color=yellow max_drones=2]
hub: path_a 2 1 [color=blue]
hub: path_b 2 -1 [color=blue]
end_hub: goal 3 0 [color=red]

connection: start-junction [max_link_capacity=2]
connection: junction-path_a
connection: junction-path_b
connection: path_a-goal
connection: path_b-goal
```

Running `python3 main.py maps/easy/02_simple_fork.txt` produces:

```
D1-junction D2-junction
D1-path_a D2-path_b D3-junction D4-junction
D1-goal D2-goal D3-path_a D4-path_b
D3-goal D4-goal
```

All 4 drones reach `goal` in 4 turns, with drones distributed across
both `path_a` and `path_b` in parallel rather than queuing on a single
route.

### Error handling example

Given a map file where the input is malformed:

```
nb_drones: 5
start_hub: start 0 0
hub: roof-1 3 4
```

Running `python3 main.py` against this file produces:

```
Error: Line (3): Invalid zone name 'roof-1': dashes are not allowed.
```