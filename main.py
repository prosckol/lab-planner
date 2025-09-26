import numpy as np
from layout import LaboratoryPlanner
from order import OrderPlanner
from operator_module import LaboratoryOperator

def main():
    rows = 36
    cols = int(16 * rows / 9)
    try:
        num_rooms = int(input("Enter number of rooms (4x4) to place: "))
    except ValueError:
        print("Invalid input, please enter an integer.")
        return

    lab_planner = LaboratoryPlanner(rows, cols)
    lab_planner.generate_layout(num_rooms)
    np.savetxt('matrix_layout.txt', lab_planner.matrix, fmt='%d')
    lab_planner.calculate_complexity()
    order_planner = OrderPlanner(lab_planner)
    order_planner.generate_orders()
    operator = LaboratoryOperator(lab_planner, order_planner)
    operator.simulate_delivery()

if __name__ == "__main__":
    main()
