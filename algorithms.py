import numpy as np

def heuristic(a, b):
    """Manhattan distance heuristic for A* pathfinding."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star_path(matrix, start, end):
    """A* algorithm for shortest path finding in grid.
    
    Args:
        matrix (np.ndarray): 2D grid with obstacles as 1.
        start (tuple): Start coordinate (row, col).
        end (tuple): End coordinate (row, col).
        
    Returns:
        list: List of coordinates representing path or None.
    """
    open_list = [(0, start[0], start[1])]
    came_from = {}
    cost_so_far = {start: 0}

    while open_list:
        open_list.sort(key=lambda x: x[0])  # Sort by priority
        current_priority, current_r, current_c = open_list.pop(0)

        if (current_r, current_c) == end:
            break

        for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            next_r, next_c = current_r + dr, current_c + dc
            if 0 <= next_r < matrix.shape[0] and 0 <= next_c < matrix.shape[1]:
                if matrix[next_r][next_c] == 1:
                    continue
                new_cost = cost_so_far[(current_r, current_c)] + 1
                if (next_r, next_c) not in cost_so_far or new_cost < cost_so_far[(next_r, next_c)]:
                    cost_so_far[(next_r, next_c)] = new_cost
                    priority = new_cost + heuristic(end, (next_r, next_c))
                    open_list.append((priority, next_r, next_c))
                    came_from[(next_r, next_c)] = (current_r, current_c)

    current = end
    path = []
    while current != start:
        path.append(current)
        if current not in came_from:
            return None
        current = came_from[current]
    path.append(start)
    path.reverse()
    return path
