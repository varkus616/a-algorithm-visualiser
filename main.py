import heapq
import pygame
import sys
import random

pygame.init()

SPRITE_SIZE = 16
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Pygame Loop Example")
font = pygame.font.Font(None, 12)

white = (255, 255, 255)
black = (0, 0, 0)
blue = (0, 0, 255)
green = (0, 255, 0)
running = True
randomize = False
place_block_flag = False
diagonal_flag = False
last_mouse_grid_pos = None

clock = pygame.time.Clock()
FPS = 60

GRID_ROWS = screen_height // SPRITE_SIZE
GRID_COLS = screen_width // SPRITE_SIZE
squares = []

grid = [[1] * GRID_COLS for _ in range(GRID_ROWS)]

grid[5][10] = 1
grid[5][11] = 1
grid[5][12] = 1
grid[5][13] = 1

def draw_grid(grid):
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            color = black
            rect = pygame.Rect(col * SPRITE_SIZE, row * SPRITE_SIZE, SPRITE_SIZE, SPRITE_SIZE)
            if grid[row][col] == 1:
                color = (255,0,0)
                pygame.draw.rect(screen, color, rect)
            else:
                pygame.draw.rect(screen, color, rect, 1)

                index_text = font.render(f"{col},{row}", True, black)
                text_rect = index_text.get_rect(center=rect.center)
                screen.blit(index_text, text_rect.topleft)


class Square:
    def __init__(self, position, color=(0, 0, 255)):
        self.position = position
        self.path = []
        self.velocity = (0, 0)
        self.speed = 5
        self.color = color

    def draw(self):
        pygame.draw.rect(screen, self.color, (*self.position, SPRITE_SIZE, SPRITE_SIZE))

    def draw_path(self):
        if self.path:
            for i in range(len(self.path) - 1):
                start_pos = (self.path[i][0] + SPRITE_SIZE // 2, self.path[i][1] + SPRITE_SIZE // 2)
                end_pos = (self.path[i + 1][0] + SPRITE_SIZE // 2, self.path[i + 1][1] + SPRITE_SIZE // 2)
                pygame.draw.line(screen, green, start_pos, end_pos, 5)

    def update(self):
        if self.path:
            target = self.path[0]
            dir_x = target[0] - self.position[0]
            dir_y = target[1] - self.position[1]
            distance = int(((dir_x ** 2 + dir_y ** 2) ** 0.5) * 0.1)
            if distance < 1:
                self.path.pop(0)
            else:
                self.velocity = ((dir_x / distance), (dir_y / distance))
                self.position = (self.position[0] + self.velocity[0], self.position[1] + self.velocity[1])


def render(grid):
    screen.fill(white)
    draw_grid(grid)
    for square in squares:
        square.draw_path()
    for square in squares:
        square.draw()
    pygame.display.flip()


def update():
    if randomize:
        randomize_squares(amount=24)
    for square in squares:
        square.update()


def world_to_grid(game_pos, cell_size):
    x, y = game_pos
    cell_width, cell_height = cell_size
    grid_x = x // cell_width
    grid_y = y // cell_height
    return (int(grid_y), int(grid_x))


def grid_to_world(grid_pos, cell_size):
    row, col = grid_pos
    cell_width, cell_height = cell_size
    x = col * cell_width
    y = row * cell_height
    return (x, y)


def heuristic(a, b):
    # a = grid_to_world(a, (SPRITE_SIZE, SPRITE_SIZE))
    # b = grid_to_world(b, (SPRITE_SIZE, SPRITE_SIZE))
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def a_star_search(grid, start, goal, diagonal=False):
    neighbors = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    diagonal_neighbors = [(1, 1), (-1, 1), (1, -1), (-1, -1)]
    if diagonal:
        neighbors.extend(diagonal_neighbors)
    close_set = set()
    came_from = {}
    gscore = {start: 0}
    fscore = {start: heuristic(start, goal)}
    oheap = []

    heapq.heappush(oheap, (fscore[start], start))

    while oheap:
        current = heapq.heappop(oheap)[1]

        if current == goal:
            data = []
            while current in came_from:
                data.append(current)
                current = came_from[current]
            return data[::-1]

        close_set.add(current)
        for i, j in neighbors:
            neighbor = current[0] + i, current[1] + j
            tentative_g_score = gscore[current] + 1
            if 0 <= neighbor[0] < len(grid):
                if 0 <= neighbor[1] < len(grid[0]):
                    if grid[neighbor[0]][neighbor[1]] == 1:
                        continue
                else:
                    continue
            else:
                continue

            if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
                continue

            if tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [i[1] for i in oheap]:
                came_from[neighbor] = current
                gscore[neighbor] = tentative_g_score
                fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(oheap, (fscore[neighbor], neighbor))

    return None


def randomize_squares(amount):
    squares.clear()
    for _ in range(amount):
        col = random.randint(0, GRID_COLS - 1)
        row = random.randint(0, GRID_ROWS - 1)
        while grid[row][col] != 0:
            col = random.randint(0, GRID_COLS - 1)
            row = random.randint(0, GRID_ROWS - 1)

        position = (col * SPRITE_SIZE, row * SPRITE_SIZE)
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        color = (r, g, b)
        squares.append(Square(position, color))


def place_block(mouse_grid_pos):
    my, mx = mouse_grid_pos
    if 0 <= my < GRID_ROWS and 0 <= mx < GRID_COLS:
        if grid[my][mx] == 0:
            grid[my][mx] = 1
        else:
            grid[my][mx] = 0


def generate_maze(x, y, speed):
    directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
    random.shuffle(directions)

    for dx, dy in directions:
        nx, ny = x + dx, y + dy

        if 0 <= nx < GRID_ROWS and 0 <= ny < GRID_COLS and grid[nx][ny] == 1:
            grid[x + dx // 2][y + dy // 2] = 0
            grid[nx][ny] = 0
            render(grid)
            pygame.time.wait(speed)
            generate_maze(nx, ny, speed)


def create_maze(speed=20):
    squares.clear()
    for x in range(GRID_ROWS):
        for y in range(GRID_COLS):
            grid[x][y] = 1
    start_x, start_y = random.choice(range(0, GRID_ROWS, 2)), random.choice(range(0, GRID_COLS, 2))
    grid[start_x][start_y] = 0
    generate_maze(start_x, start_y, 100//speed)



create_maze()


while running:
    mouse_pos = pygame.mouse.get_pos()
    mouse_grid_pos = world_to_grid(mouse_pos, (SPRITE_SIZE, SPRITE_SIZE))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            print(f"MOUSE:({mouse_pos}) GRID:({mouse_grid_pos})")
            if pygame.mouse.get_pressed()[0]:
                for square in squares:
                    start_grid_pos = world_to_grid(square.position, (SPRITE_SIZE, SPRITE_SIZE))
                    print(f"SQUARE_POS:{start_grid_pos}")
                    path = a_star_search(grid, start_grid_pos, mouse_grid_pos, diagonal_flag)
                    if path:
                        square.path = [grid_to_world(pos, (SPRITE_SIZE, SPRITE_SIZE)) for pos in path]
            elif pygame.mouse.get_pressed()[2]:
                place_block_flag = True
                last_mouse_grid_pos = mouse_grid_pos
        if event.type == pygame.MOUSEBUTTONUP:
            place_block_flag = False
            last_mouse_grid_pos = None
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                if diagonal_flag:
                    diagonal_flag = False
                else:
                    diagonal_flag = True
            if event.key == pygame.K_r:
                randomize = True
            if event.key == pygame.K_w:
                create_maze()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_r:
                randomize = False

    if place_block_flag:
        if mouse_grid_pos != last_mouse_grid_pos:
            place_block(mouse_grid_pos)
            last_mouse_grid_pos = mouse_grid_pos

    update()
    render(grid)
    clock.tick(FPS)

pygame.quit()
sys.exit()
