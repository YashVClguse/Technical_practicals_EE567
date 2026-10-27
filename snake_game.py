
import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Window settings
CELL_SIZE = 20
COLS = 30
ROWS = 25
WIDTH = COLS * CELL_SIZE
HEIGHT = ROWS * CELL_SIZE
TOP_BAR = 50

screen = pygame.display.set_mode((WIDTH, HEIGHT + TOP_BAR))
pygame.display.set_caption("Snake Game")

# Colors
BLACK = (18, 18, 24)
WHITE = (245, 245, 245)
GREEN = (60, 210, 100)
DARK_GREEN = (25, 150, 75)
RED = (240, 65, 75)
GRAY = (45, 45, 55)
YELLOW = (255, 210, 80)

# Fonts and clock
font = pygame.font.SysFont("arial", 24, bold=True)
small_font = pygame.font.SysFont("arial", 18)
clock = pygame.time.Clock()

# Movement directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


def spawn_food(snake):
    """Return a random food position not occupied by the snake."""
    while True:
        position = (
            random.randrange(COLS),
            random.randrange(ROWS)
        )
        if position not in snake:
            return position


def reset_game():
    """Initialize or restart the game."""
    snake = [(COLS // 2, ROWS // 2),
             (COLS // 2 - 1, ROWS // 2),
             (COLS // 2 - 2, ROWS // 2)]

    return snake, RIGHT, RIGHT, spawn_food(snake), 0, False


def draw_cell(position, color):
    x, y = position
    rect = pygame.Rect(
        x * CELL_SIZE,
        TOP_BAR + y * CELL_SIZE,
        CELL_SIZE,
        CELL_SIZE
    )
    pygame.draw.rect(screen, color, rect.inflate(-2, -2),
                     border_radius=4)


def draw_game(snake, food, score):
    screen.fill(BLACK)

    # Score bar
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (15, 10))

    help_text = small_font.render(
        "Arrows/WASD: Move   P: Pause   R: Restart   Esc: Quit",
        True, YELLOW
    )
    screen.blit(help_text, (150, 17))

    # Grid
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(
            screen, GRAY,
            (x, TOP_BAR), (x, HEIGHT + TOP_BAR)
        )

    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(
            screen, GRAY,
            (0, y + TOP_BAR), (WIDTH, y + TOP_BAR)
        )

    # Food and snake
    draw_cell(food, RED)

    for index, segment in enumerate(snake):
        draw_cell(segment, GREEN if index == 0 else DARK_GREEN)

    pygame.display.flip()


def show_message(title, subtitle):
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    title_surface = font.render(title, True, WHITE)
    subtitle_surface = small_font.render(subtitle, True, YELLOW)

    screen.blit(
        title_surface,
        title_surface.get_rect(
            center=(WIDTH // 2, (HEIGHT + TOP_BAR) // 2 - 20)
        )
    )
    screen.blit(
        subtitle_surface,
        subtitle_surface.get_rect(
            center=(WIDTH // 2, (HEIGHT + TOP_BAR) // 2 + 20)
        )
    )
    pygame.display.flip()


# Start game
snake, direction, next_direction, food, score, game_over = reset_game()
paused = False
running = True
move_timer = 0
MOVE_DELAY = 120  # milliseconds between movements

while running:
    clock.tick(60)

    # Handle keyboard and window events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            elif event.key == pygame.K_r:
                snake, direction, next_direction, food, score, game_over = reset_game()
                paused = False
                move_timer = 0

            elif event.key == pygame.K_p and not game_over:
                paused = not paused

            elif not game_over and not paused:
                # Prevent reversing directly into the snake
                if event.key in (pygame.K_UP, pygame.K_w):
                    if direction != DOWN:
                        next_direction = UP

                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    if direction != UP:
                        next_direction = DOWN

                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    if direction != RIGHT:
                        next_direction = LEFT

                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    if direction != LEFT:
                        next_direction = RIGHT

    if not game_over and not paused:
        move_timer += clock.get_time()

        if move_timer >= MOVE_DELAY:
            move_timer = 0
            direction = next_direction

            head_x, head_y = snake[0]
            dx, dy = direction
            new_head = (head_x + dx, head_y + dy)

            eating = new_head == food

            # If not eating, the tail moves away this turn.
            body_to_check = snake if eating else snake[:-1]

            # Wall and self-collision detection
            wall_collision = (
                new_head[0] < 0 or new_head[0] >= COLS
                or new_head[1] < 0 or new_head[1] >= ROWS
            )

            self_collision = new_head in body_to_check

            if wall_collision or self_collision:
                game_over = True
            else:
                snake.insert(0, new_head)

                if eating:
                    score += 10

                    if len(snake) < COLS * ROWS:
                        food = spawn_food(snake)
                    else:
                        game_over = True
                else:
                    snake.pop()

    draw_game(snake, food, score)

    if paused:
        show_message("PAUSED", "Press P to resume")
    elif game_over:
        show_message("GAME OVER", "Press R to restart or Esc to quit")

pygame.quit()
sys.exit()
