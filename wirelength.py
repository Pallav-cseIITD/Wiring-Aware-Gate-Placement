import math
def calculate_total_wire_length(dimensions_file, coordinates_file):
    with open(dimensions_file, 'r') as f:
        input_data = f.readlines()

    with open(coordinates_file, 'r') as f:
        output_data = f.readlines()

    gates = {}
    pins = {}
    wires = []

    for line in input_data:
        tokens = line.split()
        if tokens[0].startswith('g'):
            gate_name = tokens[0]
            width, height = int(tokens[1]), int(tokens[2])
            gates[gate_name] = {"width": width, "height": height}
        elif tokens[0] == "pins":
            gate_name = tokens[1]
            pin_coords = [(int(tokens[i]), int(tokens[i + 1])) for i in range(2, len(tokens), 2)]
            pins[gate_name] = pin_coords
        elif tokens[0] == "wire":
            wire_from = tokens[1].split('.')
            wire_to = tokens[2].split('.')
            wires.append((wire_from, wire_to))

    gate_positions = {}
    for line in output_data:
        tokens = line.split()
        if tokens[0].startswith('g'):
            gate_name = tokens[0]
            x, y = int(tokens[1]), int(tokens[2])
            gate_positions[gate_name] = (x, y)

    pin_positions = {}
    for gate, position in gate_positions.items():
        gate_x, gate_y = position
        pin_positions[gate] = [(gate_x + px, gate_y + py) for (px, py) in pins[gate]]

    all_pins = []
    pin_names = []
    gate_names = []

    for gate, pin_list in pin_positions.items():
        for i, pin_coords in enumerate(pin_list):
            pin_name = f"{gate}.p{i + 1}"
            all_pins.append(pin_coords)
            pin_names.append(pin_name)
            gate_names.append(gate)

    distance_matrix = [[0] * len(all_pins) for _ in range(len(all_pins))]
    for i in range(len(all_pins)):
        for j in range(len(all_pins)):
            if i != j:
                if gate_names[i] == gate_names[j]:
                    distance_matrix[i][j] = math.inf
                else:
                    distance_matrix[i][j] = abs(all_pins[i][0] - all_pins[j][0]) + abs(all_pins[i][1] - all_pins[j][1])

    connection_matrix = [[False] * len(pin_names) for _ in range(len(pin_names))]
    for wire in wires:
        gate1, pin1 = wire[0]
        gate2, pin2 = wire[1]
        pin1_idx = int(pin1[1:]) - 1
        pin2_idx = int(pin2[1:]) - 1
        pin1_full = f"{gate1}.p{pin1_idx + 1}"
        pin2_full = f"{gate2}.p{pin2_idx + 1}"

        if pin1_full in pin_names and pin2_full in pin_names:
            idx1 = pin_names.index(pin1_full)
            idx2 = pin_names.index(pin2_full)
            connection_matrix[idx1][idx2] = True

    total_wire_length = 0
    ordered_pin_coordinates = [pin for pin_list in pin_positions.values() for pin in pin_list]

    for i in range(len(connection_matrix)):
        if True in connection_matrix[i]:
            bounding_x = []
            bounding_y = []
            bounding_x.append(ordered_pin_coordinates[i][0])
            bounding_y.append(ordered_pin_coordinates[i][1])

            for j in range(len(connection_matrix[i])):
                if connection_matrix[i][j]:
                    bounding_x.append(ordered_pin_coordinates[j][0])
                    bounding_y.append(ordered_pin_coordinates[j][1])

            xmin = min(bounding_x)
            xmax = max(bounding_x)
            ymin = min(bounding_y)
            ymax = max(bounding_y)

            total_wire_length += xmax - xmin + ymax - ymin

    return total_wire_length

