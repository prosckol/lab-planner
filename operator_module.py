import pygame
import numpy as np
from algorithms import a_star_path

class LaboratoryOperator:
    """
    Handles the robot simulation: batching deliveries, pathfinding, movement, and interactions.
    """

    def __init__(self, lab_planner, order_planner):
        self.lab_planner = lab_planner
        self.order_planner = order_planner
        self.robot_pos = lab_planner.docking_center
        self.robot_path = []
        self.inventory = []
        self.batches = []
        self.current_target_room = None
        self.current_batch_idx = 0
        self.current_phase = "idle"
        self.delivering_rooms = []
        self.simulation_paused = False
        self.delivery_pause_end = 0

    def simulate_delivery(self):
        # Initialize pygame display and load images
        pygame.init()
        cell_size = 21
        width, height = self.lab_planner.cols * cell_size, self.lab_planner.rows * cell_size
        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Laboratory Layout Planner and Operator")
        font = pygame.font.SysFont('Arial', 12)
        COLORS = {
            0: (255, 255, 255),
            1: (0, 0, 0),
            4: (0, 255, 0),
            'dark_green': (0, 100, 0),
            2: (200, 200, 200),
            3: (150, 75, 0),
            5: (0, 0, 255)
        }

        def load_image(path, size):
            try:
                img = pygame.image.load(path)
                return pygame.transform.scale(img, (size[0]*cell_size, size[1]*cell_size))
            except Exception as e:
                return pygame.Surface((size[0]*cell_size, size[1]*cell_size))

        img_2 = load_image("images/2_cluster.png", (6, 6))
        img_3 = load_image("images/3_cluster.png", (2, 5))
        img_5 = load_image("images/5_cluster.png", (4, 4))
        robot_img = load_image("images/robot.png", (1, 1))

        # Prepare delivery batches by room priority
        all_items = []
        priority_map = {}
        for room in self.order_planner.room_data:
            if room['reachable'] and room['orders']:
                for item in room['orders']:
                    all_items.append((item, room['position']))
                priority_map[room['position']] = room['priority']
        sorted_rooms = sorted(list(set([item[1] for item in all_items])), key=lambda x: priority_map[x] or 10)
        sorted_items = []
        for room in sorted_rooms:
            sorted_items.extend([item for item in all_items if item[1] == room])
        batch_size = 10
        self.batches = [sorted_items[i:i+batch_size] for i in range(0, len(sorted_items), batch_size)]

        clock = pygame.time.Clock()
        running = True
        show_inventory = False

        while running:
            current_time = pygame.time.get_ticks()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_l:
                        show_inventory = not show_inventory
                    if event.key == pygame.K_s:
                        pygame.image.save(screen, 'simulation_snapshot.png')
                    if event.key == pygame.K_SPACE:
                        self.simulation_paused = not self.simulation_paused

            if not self.simulation_paused and current_time >= self.delivery_pause_end:
                self._simulate_step()

            self._draw_simulation(screen, font, cell_size, COLORS, img_2, img_3, img_5, robot_img, show_inventory)
            pygame.display.update()
            clock.tick(10)

        pygame.quit()

    def _simulate_step(self):
        # Manages path and robot actions between deliveries and pickups
        if not self.robot_path:
            if self.current_phase == "idle" and self.current_batch_idx < len(self.batches):
                path = a_star_path(self.lab_planner.matrix, self.robot_pos, self.lab_planner.warehouse_center)
                if path:
                    self.robot_path = path[1:]
                    self.current_phase = "to_warehouse"
            elif self.current_phase == "to_warehouse":
                current_batch = self.batches[self.current_batch_idx]
                self.inventory = current_batch.copy()
                self.current_batch_idx += 1
                room_items = {}
                for item, pos in current_batch:
                    if pos not in room_items:
                        room_items[pos] = []
                    room_items[pos].append(item)
                self.delivering_rooms = list(room_items.keys())
                self.current_phase = "delivering"
            elif self.current_phase == "delivering":
                if self.delivering_rooms:
                    room_pos = self.delivering_rooms.pop(0)
                    self.current_target_room = room_pos
                    room_center = (room_pos[0] + 2, room_pos[1] + 2)
                    path = a_star_path(self.lab_planner.matrix, self.robot_pos, room_center)
                    if path:
                        self.robot_path = path[1:]
                    else:
                        self.delivering_rooms = []
                else:
                    if self.current_batch_idx < len(self.batches):
                        path = a_star_path(self.lab_planner.matrix, self.robot_pos, self.lab_planner.warehouse_center)
                        if path:
                            self.robot_path = path[1:]
                            self.current_phase = "to_warehouse"
                    else:
                        path = a_star_path(self.lab_planner.matrix, self.robot_pos, self.lab_planner.docking_center)
                        if path:
                            self.robot_path = path[1:]
                            self.current_phase = "returning"
            elif self.current_phase == "returning":
                self.current_phase = "done"
        else:
            next_pos = self.robot_path.pop(0)
            self.robot_pos = (next_pos[0], next_pos[1])
            if not self.robot_path and self.current_phase == "delivering":
                self.delivery_pause_end = pygame.time.get_ticks() + 1000
                if self.current_target_room:
                    items_delivered = [item for item, pos in self.inventory if pos == self.current_target_room]
                    for room in self.order_planner.room_data:
                        if room['position'] == self.current_target_room:
                            room['orders'] = [item for item in room['orders'] if item not in items_delivered]
                    self.inventory = [(item, pos) for (item, pos) in self.inventory if pos != self.current_target_room]
                    self.current_target_room = None

    def _draw_simulation(self, screen, font, cell_size, COLORS, img_2, img_3, img_5, robot_img, show_inventory):
        # Draws the simulation state including the map, robot, and overlays
        screen.fill((50, 50, 50))
        for y in range(self.lab_planner.rows):
            for x in range(self.lab_planner.cols):
                val = self.lab_planner.matrix[y][x]
                color = COLORS.get(val, (255, 255, 255))
                if self.current_target_room and val == 4:
                    ry, rx = self.current_target_room
                    if ry <= y < ry + 4 and rx <= x < rx + 4:
                        color = COLORS['dark_green']
                pygame.draw.rect(screen, color, (x * cell_size, y * cell_size, cell_size, cell_size))
        screen.blit(img_2, ((self.lab_planner.cols - 6) * cell_size, (self.lab_planner.rows - 6) * cell_size))
        screen.blit(img_3, (0, 0))
        screen.blit(img_5, ((self.lab_planner.cols // 2 - 2) * cell_size, (self.lab_planner.rows - 4) * cell_size))
        robot_x = self.robot_pos[1] * cell_size
        robot_y = self.robot_pos[0] * cell_size
        screen.blit(robot_img, (robot_x, robot_y))
        if show_inventory and self.inventory:
            items = [f"{i+1}. {item[0]}" for i, item in enumerate(self.inventory)]
            line_height = font.get_height()
            padding = 5
            total_height = len(items) * line_height + 2 * padding
            max_width = max([font.size(item)[0] for item in items]) + 2 * padding
            bg_rect = pygame.Rect(robot_x + cell_size + 5, robot_y - padding, max_width, total_height)
            if bg_rect.right > screen.get_width():
                bg_rect.right = robot_x - 5
            pygame.draw.rect(screen, (255, 255, 255), bg_rect)
            y_pos = bg_rect.top + padding
            for item in items:
                text = font.render(item, True, (0, 0, 0))
                screen.blit(text, (bg_rect.left + padding, y_pos))
                y_pos += line_height
        if show_inventory:
            for room in self.order_planner.room_data:
                if room['orders']:
                    start_row, start_col = room['position']
                    x = start_col * cell_size
                    y_pos = start_row * cell_size
                    orders = room['orders']
                    reachable = room['reachable']
                    priority = room['priority']
                    text_lines = []
                    if priority is not None:
                        text_lines.append(f"Priority: {priority}")
                    text_lines += orders[:2]
                    if not reachable:
                        text_lines = ["Unreachable!"] + text_lines
                    line_height = font.get_height()
                    total_height = line_height * len(text_lines)
                    text_bg = pygame.Surface((4 * cell_size, total_height), pygame.SRCALPHA)
                    text_color = (255, 0, 0) if not reachable else (0, 0, 0)
                    y_offset = 0
                    for line in text_lines:
                        text = font.render(line, True, text_color)
                        text_rect = text.get_rect(center=(2 * cell_size, y_offset + line_height // 2))
                        text_bg.blit(text, text_rect)
                        y_offset += line_height
                    text_y = y_pos + (4 * cell_size - total_height) // 2
                    screen.blit(text_bg, (x, text_y))
