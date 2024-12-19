import random
import math
import time
from multiprocessing import Pool, cpu_count
from wirelength import *

def read_input(file):
    gates = {}
    wires = []

    with open(file, 'r') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("g"):
            parts = line.split()
            gate_name = parts[0]
            gate = {'width': int(parts[1]), 'height': int(parts[2]), 'pins': []}
            i += 1
            line = lines[i].strip()
            if line.startswith("pins"):
                pin_parts = line.split()[2:]
                gate['pins'] = [(int(pin_parts[j]), int(pin_parts[j + 1])) for j in range(0, len(pin_parts), 2)]
            gates[gate_name] = gate
        elif line.startswith("wire"):
            wire_parts = line.split()
            wires.append(
                (wire_parts[1].split('.')[0], int(wire_parts[1].split('.')[1][1:]),
                 wire_parts[2].split('.')[0], int(wire_parts[2].split('.')[1][1:]))
            )
        i += 1
    return gates, wires

def find_valid_points(skyline, box_width):
    points = []
    prev = skyline[0]

    for i in range(1, box_width):
        if skyline[i] != prev:
            points.append([0 if prev > skyline[i] else 1, i, skyline[i]])
        prev = skyline[i]

    points.append([1, box_width, skyline[-1]])
    return points

def update_skyline(skyline, point, rect_height, rect_width):
    start = point[1] - rect_width if point[0] else point[1]
    skyline[start:start + rect_width] = [point[2] + rect_height] * rect_width
    return skyline

def is_valid_placement(rect_height, rect_width, point, skyline):
    try:
        start = point[1] - rect_width if point[0] else point[1]
        return all(skyline[i] <= point[2] for i in range(start, start + rect_width))
    except IndexError:
        return False

def pack_rectangles(rectangle_sequence, box_width):
    skyline = [0] * box_width
    placements = []

    for rectangle in rectangle_sequence:
        for point in sorted(find_valid_points(skyline, box_width), key=lambda x: (x[2], x[1])):
            if is_valid_placement(rectangle[2], rectangle[1], point, skyline):
                x_pos = point[1] - rectangle[1] if point[0] else point[1]
                placements.append([rectangle[0], x_pos, point[2]])
                update_skyline(skyline, point, rectangle[2], rectangle[1])
                break

    return placements, max(skyline)

def manhattan_distance(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2)
def total_wire_length(gate_positions, wires, gates_dict):
    wire_length = 0

    # Calculate the total wire length based on the wires and gate positions
    for wire in wires:
        gate1, pin1, gate2, pin2 = wire

        g1_x, g1_y = gate_positions.get(gate1, (None, None))
        g2_x, g2_y = gate_positions.get(gate2, (None, None))

        if g1_x is None or g2_x is None:
            print(f"Warning: Gate {gate1} or {gate2} is missing in the positions.")
            continue

        if pin1 > len(gates_dict[gate1]['pins']) or pin1 <= 0:
            print(f"Warning: Invalid pin index {pin1} for gate {gate1}")
            continue
        if pin2 > len(gates_dict[gate2]['pins']) or pin2 <= 0:
            print(f"Warning: Invalid pin index {pin2} for gate {gate2}")
            continue

        p1_x, p1_y = gates_dict[gate1]['pins'][pin1 - 1]
        p2_x, p2_y = gates_dict[gate2]['pins'][pin2 - 1]

        pin1_pos = (g1_x + p1_x, g1_y + p1_y)
        pin2_pos = (g2_x + p2_x, g2_y + p2_y)

        distance = abs(pin1_pos[0] - pin2_pos[0]) + abs(pin1_pos[1] - pin2_pos[1])
        wire_length += distance

    return wire_length


def generate_neighbor(gate_positions, grid_size, gates, gates_dict):
    new_positions = gate_positions.copy()
    gate_to_move = random.choice(list(new_positions.keys()))
    current_x, current_y = new_positions[gate_to_move]

    delta_x = random.randint(-5, 5)
    delta_y = random.randint(-5, 5)

    new_x = max(0, min(current_x + delta_x, grid_size[0] - gates_dict[gate_to_move]['width']))
    new_y = max(0, min(current_y + delta_y, grid_size[1] - gates_dict[gate_to_move]['height']))

    new_positions[gate_to_move] = (new_x, new_y)
    return new_positions

def no_gate_overlap(gate_positions, gates_dict):
    positions = [(gate, *gate_positions[gate], gates_dict[gate]['width'], gates_dict[gate]['height'])
                 for gate in gate_positions]

    for i, (g1, x1, y1, w1, h1) in enumerate(positions):
        for g2, x2, y2, w2, h2 in positions[i + 1:]:
            if not (x1 + w1 <= x2 or x1 >= x2 + w2 or y1 + h1 <= y2 or y1 >= y2 + h2):
                return False
    return True


def simulated_annealing(gates, wires, grid_size, initial_temp, final_temp, alpha, num_neighbors):
    sorted_gates = sorted(gates.values(), key=lambda g: (g['height'], g['width']), reverse=True)
    gate_sequence = [(name, gate['width'], gate['height']) for name, gate in gates.items()]

    # Initial solution using skyline heuristic
    initial_placements, _ = pack_rectangles(gate_sequence, grid_size[0])
    gate_positions = {placement[0]: (placement[1], placement[2]) for placement in initial_placements}

    gates_dict = {gate: gates[gate] for gate in gates}
    current_solution = gate_positions
    current_wire_length = total_wire_length(gate_positions, wires, gates_dict)
    current_temp = initial_temp

    while current_temp > final_temp:
        for _ in range(num_neighbors):
            new_solution = generate_neighbor(current_solution, grid_size, gates, gates_dict)
            if no_gate_overlap(new_solution, gates_dict):
                new_wire_length = total_wire_length(new_solution, wires, gates_dict)
                delta_length = new_wire_length - current_wire_length

                if delta_length < 0 or random.uniform(0, 1) < math.exp(-delta_length / current_temp):
                    current_solution = new_solution
                    current_wire_length = new_wire_length

        current_temp *= alpha

    return current_solution, current_wire_length

def parallel_simulated_annealing(gates, wires, grid_size, initial_temp, final_temp, alpha, num_iterations,
                                 num_neighbors):
    num_workers = cpu_count()
    with Pool(num_workers) as pool:
        results = pool.starmap(simulated_annealing,
                               [(gates, wires, grid_size, initial_temp, final_temp, alpha,
                                 num_neighbors)] * num_iterations)

    return min(results, key=lambda x: x[1])

def write_output(output_file, final_solution, gates_dict, best_wire_length):
    min_x = min(x for x, y in final_solution.values())
    min_y = min(y for x, y in final_solution.values())

    shifted_positions = {gate: (x - min_x, y - min_y) for gate, (x, y) in final_solution.items()}
    max_x = max(x + gates_dict[gate]['width'] for gate, (x, y) in shifted_positions.items())
    max_y = max(y + gates_dict[gate]['height'] for gate, (x, y) in shifted_positions.items())

    with open(output_file, 'w') as f:
        f.write(f"bounding_box {max_x} {max_y}\n")
        for gate, (x, y) in shifted_positions.items():
            f.write(f"{gate} {x} {y}\n")
        f.write(f"wire_length {best_wire_length}")

if __name__ == "__main__":
    st = time.perf_counter()
    gates, wires = read_input("input.txt")
    gates_num = len(gates)
    wire_num = len(wires)
    grid_size = (5000, 5000)
    initial_temp = 1000
    final_temp = 0.01
    alpha = 0.99
    num_iterations = 10
    num_neighbors = 100

    if gates_num > 400 or wire_num > 500:
        alpha = 0.92
        final_temp = 0.01

    if gates_num < 30 or wire_num < 50:
        alpha = 0.999
        final_temp = 0.001

    best_solution, best_wire_length = parallel_simulated_annealing(
        gates, wires, grid_size, initial_temp, final_temp, alpha, num_iterations, num_neighbors
    )

    write_output("output.txt", best_solution, gates, best_wire_length)
    wire_length = calculate_total_wire_length("input.txt","output.txt")
    write_output("output.txt", best_solution, gates, wire_length)
    et = time.perf_counter()
    print(f"Wire length: {wire_length} units")
    print(f"Execution time: {et - st:.2f} seconds")
