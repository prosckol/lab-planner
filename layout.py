import numpy as np
import random
from algorithms import a_star_path

class LaboratoryPlanner:
    """Creates laboratory layout grid with rooms, obstacles, warehouse, and docking station."""

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.matrix = np.zeros((rows, cols), dtype=int)
        self.rooms = []
        self.num_obstacles = 0
        self.docking_center = None
        self.warehouse_center = None
        self.minimal_path = 0
        self.average_path = 0
        self.unreachable_rooms = []
        self.warehouse_accessible = False

    def generate_layout(self, num_rooms):
        """Place warehouse, stairs, docking station, rooms, and random obstacles."""
        self.matrix[-6:, -6:] = 2
        self.matrix[0:5, 0:2] = 3
        mid_bottom_row = self.rows - 4
        mid_bottom_col = self.cols // 2 - 2
        self.matrix[mid_bottom_row:mid_bottom_row+4, mid_bottom_col:mid_bottom_col+4] = 5
        self.rooms = self._place_rooms(num_rooms)
        placed_rooms = len(self.rooms)
        if placed_rooms < num_rooms:
            print(f"Warning: Only placed {placed_rooms}/{num_rooms} rooms")
        empty_cells = np.argwhere(self.matrix == 0)
        self.num_obstacles = int(0.25 * len(empty_cells))
        for i in random.sample(range(len(empty_cells)), self.num_obstacles):
            row, col = empty_cells[i]
            self.matrix[row, col] = 1
        self.docking_center = (mid_bottom_row + 2, mid_bottom_col + 2)
        self.warehouse_center = (self.rows - 3, self.cols - 3)

    def _place_rooms(self, num_rooms):
        """Randomly position rooms (clusters of '4') in the grid."""
        placed = 0
        grid_size = 6
        grid_rows = self.rows // grid_size
        grid_cols = self.cols // grid_size
        positions = [(r, c) for r in range(grid_rows) for c in range(grid_cols)]
        random.shuffle(positions)
        rooms = []
        for r, c in positions:
            if placed >= num_rooms:
                break
            jitter_r = random.randint(-2, 2)
            jitter_c = random.randint(-2, 2)
            start_row = max(1, min(self.rows-5, r * grid_size + jitter_r))
            start_col = max(1, min(self.cols-5, c * grid_size + jitter_c))
            if np.all(self.matrix[start_row-1:start_row+5, start_col-1:start_col+5] == 0):
                self.matrix[start_row:start_row+4, start_col:start_col+4] = 4
                rooms.append((start_row, start_col))
                placed += 1
        return rooms

    def calculate_complexity(self):
        """Analyze pathfinding from docking station to warehouse and rooms."""
        path_to_warehouse = a_star_path(self.matrix, self.docking_center, self.warehouse_center)
        self.warehouse_accessible = path_to_warehouse is not None
        path_lengths = []
        self.unreachable_rooms = []
        for (start_row, start_col) in self.rooms:
            room_center = (start_row + 2, start_col + 2)
            path = a_star_path(self.matrix, room_center, self.docking_center)
            if path and self.warehouse_accessible:
                path_lengths.append(len(path)-1)
            else:
                self.unreachable_rooms.append((start_row, start_col))
        self.minimal_path = min(path_lengths) if path_lengths else 0
        self.average_path = sum(path_lengths)/len(path_lengths) if path_lengths else 0
        self.print_complexity_analysis()

    def print_complexity_analysis(self):
        print("\nLayout Complexity Analysis:")
        print(f"Number of rooms: {len(self.rooms)} (4x4)")
        print(f"Number of obstacles: {self.num_obstacles} (1x1)")
        print(f"Minimal path length: {self.minimal_path}")
        print(f"Average path length: {self.average_path:.2f}")
        if not self.warehouse_accessible:
            print("No valid path between docking station and warehouse!")
            print("Robot cannot collect items.")
        elif self.unreachable_rooms:
            print("Unreachable Rooms:")
            for room in self.unreachable_rooms:
                print(f"- Room at (row={room[0]}, column={room[1]})")
        else:
            print("All rooms are reachable!")
