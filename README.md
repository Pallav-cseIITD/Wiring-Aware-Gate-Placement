# Wiring-Aware-Gate-Placement
**Wiring-Aware Gate Placement Optimization**

**Introduction**  
This project involves designing a circuit layout with rectangular logic gates and their associated pins to minimize the total wire length of the connections. The goal is to determine the optimal positions for gates on a plane while ensuring no overlaps and using the semi-perimeter method to estimate wire lengths.

**Problem Description**

1.  **Given Inputs**:
    -   A set of rectangular logic gates (g1, g2, ..., gn) with specified dimensions (width and height).
    -   Pin locations on the boundary of each gate (gi.p1, gi.p2, ..., gi.pm), given as coordinates relative to the bottom-left corner of the gate.
    -   Connections between pins of different gates.
2.  **Objective**:
    -   Assign positions to all gates such that:
        -   No two gates overlap.
        -   The total estimated wire length (using the semi-perimeter method) is minimized.
3.  **Constraints**:
    -   Gates cannot be rotated or reoriented.
    -   All wiring is horizontal and vertical (Manhattan wiring).

**Solution Approach**

1.  **Mathematical Formulation**:
    -   Wire length is estimated using the Manhattan distance: f(wi)=∣xi(1)−xi(2)∣+∣yi(1)−yi(2)∣f(w_i) = \|x_i\^{(1)} - x_i\^{(2)}\| + \|y_i\^{(1)} - y_i\^{(2)}\|
    -   Total wire length is the sum of distances for all wires: Total Wire Length=∑i=1mf(wi)\\text{Total Wire Length} = \\sum_{i=1}\^m f(w_i)
    -   The semi-perimeter method forms a bounding box around connected pins and uses half its perimeter as the estimated wire length.
2.  **Algorithm Design**:
    -   **Initial Placement**:
        -   Use a greedy algorithm to place gates while avoiding overlaps.
        -   Minimize the bounding box dimensions during initial placement.
    -   **Wire Length Optimization**:
        -   Refine the initial placement using heuristics to minimize total Manhattan distances between connected pins.
3.  **Output Generation**:
    -   Output the dimensions of the bounding box, total wire length, and the positions of all gates.

**Input and Output Formats**

1.  **Input Format**:
    -   Gate dimensions:
    -   \<name of gate\> \<width\> \<height\>
    -   Pin coordinates relative to the bottom-left corner of the gate:
    -   \<pins\> \<name of gate\> \<x_1, y_1\> ... \<x_m, y_m\>
    -   Wire connections:
    -   \<wire\> \<g_x.p_x\> \<g_y.p_y\>

**Example**:

g1 2 3

pins g1 0 1 0 2

g2 3 2

pins g2 0 0 3 1

wire g1.p1 g2.p2

wire g1.p2 g2.p1

1.  **Output Format**:
    -   Bounding box dimensions and total wire length:
    -   bounding_box \<width\> \<height\>
    -   wire_length \<total_wire_length\>
    -   Gate positions:
    -   \<name of gate\> \<x-coordinate\> \<y-coordinate\>

**Example**:

bounding_box 7 3

wire_length 11

g1 0 0

g2 2 0

g3 5 0

**Testing and Constraints**

1.  **Constraints**:
    -   Number of gates: 1≤n≤10001 \\leq n \\leq 1000
    -   Gate dimensions: 1≤width, height≤1001 \\leq \\text{width, height} \\leq 100
    -   Total pins: 1≤pins≤40,0001 \\leq \\text{pins} \\leq 40,000
    -   Pins have integral coordinates.
2.  **Testing**:
    -   Verify with provided sample inputs.
    -   Generate additional test cases to handle edge scenarios and ensure correctness.

**Conclusion**  
This project demonstrates a systematic approach to minimize wiring costs in circuit layouts. By optimizing gate placements and using Manhattan distance for wire length estimation, the solution balances efficiency and practicality in wiring-aware design.
