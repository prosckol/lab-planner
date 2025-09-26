import random
from algorithms import a_star_path

class OrderPlanner:
    """Assigns room orders for items to be picked from warehouse."""

    def __init__(self, lab_planner):
        self.lab_planner = lab_planner
        self.room_data = []
        self.item_list = [
            'Masks', 'Gloves', 'Goggles', 'Lab Coats', 'Safety Glasses', 'Face Shields',
            'Hand Sanitizer', 'Disinfectant Wipes', 'First Aid Kits', 'Syringe'
        ]
        self.total_orders = 0

    def generate_orders(self):
        """Assign random orders, reachability, and priorities to rooms."""
        self.room_data = []
        self.total_orders = 0
        for (start_row, start_col) in self.lab_planner.rooms:
            room_center = (start_row + 2, start_col + 2)
            path = a_star_path(self.lab_planner.matrix, room_center, self.lab_planner.docking_center)
            is_reachable = path is not None and self.lab_planner.warehouse_accessible
            num_orders = random.choices(
                [0, 1, 2],
                weights=[7, 2.5, 0.5] if self.total_orders > 10 else [1, 1, 1],
                k=1
            )[0]
            orders = random.sample(self.item_list, num_orders) if num_orders > 0 else []
            self.total_orders += num_orders
            priority = random.randint(1, 9) if num_orders > 0 else None
            self.room_data.append({
                'position': (start_row, start_col),
                'orders': orders,
                'reachable': is_reachable,
                'priority': priority
            })
