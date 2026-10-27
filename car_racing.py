
import pygame
import random
import json
import os

pygame.init()

# -------------------- CONFIGURATION --------------------
WIDTH, HEIGHT = 600, 800
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NEON DRIVE | Car Racing")

clock = pygame.time.Clock()

# Colors
BG = (12, 16, 27)
ROAD = (38, 43, 55)
WHITE = (245, 248, 255)
GRAY = (130, 145, 165)
CYAN = (35, 225, 255)
RED = (255, 65, 95)
YELLOW = (255, 210, 70)
GREEN = (65, 240, 160)

FONT = pygame.font.SysFont("arial", 22, bold=True)
SMALL = pygame.font.SysFont("arial", 16, bold=True)
TITLE = pygame.font.SysFont("arial", 54, bold=True)
BIG = pygame.font.SysFont("arial", 32, bold=True)

# Road layout
ROAD_LEFT = 90
ROAD_RIGHT = 510
ROAD_WIDTH = ROAD_RIGHT - ROAD_LEFT
LANE_WIDTH = ROAD_WIDTH // 3
CAR_W, CAR_H = 48, 82

HIGH_SCORE_FILE = "car_racing_record.json"

# -------------------- HELPERS --------------------
def load_high_score():
    try:
        with open(HIGH_SCORE_FILE, "r") as file:
            return json.load(file).get("high_score", 0)
    except (OSError, ValueError):
        return 0


def save_high_score(score):
    try:
        with open(HIGH_SCORE_FILE, "w") as file:
            json.dump({"high_score": score}, file)
    except OSError:
        pass


def draw_text(text, font, color, x, y, center=True):
    image = font.render(str(text), True, color)
    rect = image.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(image, rect)


def draw_car(x, y, color, player=False):
    """Draw a small top-down car using Pygame shapes."""
    x, y = int(x), int(y)

    # Wheels
    for wy in (y + 15, y + 55):
        pygame.draw.rect(
            screen, (10, 12, 18),
            (x - 4, wy, 8, 18), border_radius=3
        )
        pygame.draw.rect(
            screen, (10, 12, 18),
            (x + CAR_W - 4, wy, 8, 18), border_radius=3
        )

    # Main body
    pygame.draw.rect(
        screen, color,
        (x, y, CAR_W, CAR_H), border_radius=10
    )

    # Center highlight
    highlight = tuple(min(255, c + 35) for c in color)
    pygame.draw.rect(
        screen, highlight,
        (x + 5, y + 8, CAR_W - 10, 12), border_radius=5
    )

    # Windshield
    pygame.draw.rect(
        screen, (30, 55, 78),
        (x + 7, y + 24, CAR_W - 14, 20), border_radius=5
    )
    pygame.draw.line(
        screen, (100, 180, 205),
        (x + 10, y + 27), (x + CAR_W - 10, y + 27), 2
    )

    # Rear window
    pygame.draw.rect(
        screen, (25, 45, 65),
        (x + 9, y + 53, CAR_W - 18, 10), border_radius=3
    )

    # Lights
    for lx in (x + 7, x + CAR_W - 15):
        pygame.draw.rect(
            screen, YELLOW if player else RED,
            (lx, y + (3 if player else CAR_H - 8), 8, 4),
            border_radius=2
        )

    if player:
        # Neon glow accent
        pygame.draw.line(
            screen, CYAN,
            (x + 4, y + 47), (x + 4, y + 65), 2
        )
        pygame.draw.line(
            screen, CYAN,
            (x + CAR_W - 4, y + 47),
            (x + CAR_W - 4, y + 65), 2
        )


def draw_road(offset):
    screen.fill(BG)

    # Decorative roadside lights
    for y in range(-30, HEIGHT + 30, 60):
        yy = (y + int(offset * 1.5)) % (HEIGHT + 60) - 30
        pygame.draw.circle(screen, (30, 65, 82), (35, yy), 3)
        pygame.draw.circle(screen, (30, 65, 82), (565, yy), 3)

    # Road surface
    pygame.draw.rect(
        screen, ROAD,
        (ROAD_LEFT, 0, ROAD_WIDTH, HEIGHT)
    )

    # Road shoulders
    pygame.draw.rect(
        screen, CYAN, (ROAD_LEFT, 0, 3, HEIGHT)
    )
    pygame.draw.rect(
        screen, RED, (ROAD_RIGHT - 3, 0, 3, HEIGHT)
    )

    # Roadside rumble strips
    for y in range(-40, HEIGHT, 40):
        yy = (y + int(offset)) % (HEIGHT + 40) - 40
        pygame.draw.rect(
            screen, (95, 105, 120),
            (ROAD_LEFT + 7, yy, 5, 22)
        )
        pygame.draw.rect(
            screen, (95, 105, 120),
            (ROAD_RIGHT - 12, yy, 5, 22)
        )

    # Dashed lane markings
    for lane in (1, 2):
        x = ROAD_LEFT + lane * LANE_WIDTH
        for y in range(-60, HEIGHT + 60, 90):
            yy = (y + int(offset)) % (HEIGHT + 90) - 60
            pygame.draw.rect(
                screen, (205, 215, 225),
                (x - 2, yy, 4, 48), border_radius=2
            )


def draw_panel(rect, color=(20, 27, 43)):
    pygame.draw.rect(screen, color, rect, border_radius=14)
    pygame.draw.rect(
        screen, (65, 83, 105), rect, width=1, border_radius=14
    )


# -------------------- GAME STATE --------------------
high_score = load_high_score()


def reset_game():
    return {
        "player_x": ROAD_LEFT + LANE_WIDTH + (LANE_WIDTH - CAR_W) // 2,
        "player_y": HEIGHT - 125,
        "traffic": [],
        "spawn_timer": 0,
        "road_offset": 0,
        "score": 0,
        "speed": 5.0,
        "game_over": False,
        "paused": False,
        "started": False,
    }


game = reset_game()
running = True

# -------------------- MAIN LOOP --------------------
while running:
    dt = clock.tick(FPS) / 16.667
    dt = min(dt, 2.0)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if game["game_over"]:
                    game = reset_game()
                    game["started"] = True
                else:
                    game["started"] = True

            elif event.key == pygame.K_p and game["started"]:
                if not game["game_over"]:
                    game["paused"] = not game["paused"]

    keys = pygame.key.get_pressed()

    if (
        game["started"]
        and not game["game_over"]
        and not game["paused"]
    ):
        # Player movement
        move_speed = 6.5 * dt

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            game["player_x"] -= move_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            game["player_x"] += move_speed

        # Keep the player within road boundaries
        game["player_x"] = max(
            ROAD_LEFT + 15,
            min(
                ROAD_RIGHT - CAR_W - 15,
                game["player_x"]
            )
        )

        # Difficulty progression
        game["speed"] = min(
            13.0, 5.0 + game["score"] / 300
        )

        game["road_offset"] += game["speed"] * dt

        # Spawn traffic with safe lane spacing
        game["spawn_timer"] += dt
        spawn_interval = max(31, 70 - game["score"] // 60)

        if game["spawn_timer"] >= spawn_interval:
            game["spawn_timer"] = 0

            lanes = list(range(3))
            random.shuffle(lanes)

            # Avoid spawning directly beside another new car
            chosen_lane = None
            for lane in lanes:
                lane_x = (
                    ROAD_LEFT + lane * LANE_WIDTH
                    + (LANE_WIDTH - CAR_W) // 2
                )
                blocked = any(
                    abs(car["x"] - lane_x) < LANE_WIDTH * 0.6
                    and car["y"] < 150
                    for car in game["traffic"]
                )
                if not blocked:
                    chosen_lane = lane
                    break

            if chosen_lane is not None:
                lane_x = (
                    ROAD_LEFT + chosen_lane * LANE_WIDTH
                    + (LANE_WIDTH - CAR_W) // 2
                )
                color = random.choice([
                    RED, YELLOW, (175, 100, 255),
                    (255, 140, 65), (90, 190, 255)
                ])
                game["traffic"].append({
                    "x": lane_x,
                    "y": -CAR_H - 10,
                    "color": color,
                    "speed": random.uniform(0.75, 1.25),
                    "passed": False,
                })

        # Move traffic and award points
        for car in game["traffic"]:
            car["y"] += game["speed"] * car["speed"] * dt

            if not car["passed"] and car["y"] > HEIGHT:
                car["passed"] = True
                game["score"] += 10

        game["traffic"] = [
            car for car in game["traffic"]
            if car["y"] < HEIGHT + CAR_H
        ]

        # Collision detection with a small visual margin
        player_rect = pygame.Rect(
            int(game["player_x"]) + 5,
            game["player_y"] + 6,
            CAR_W - 10,
            CAR_H - 12,
        )

        for car in game["traffic"]:
            enemy_rect = pygame.Rect(
                int(car["x"]) + 5,
                int(car["y"]) + 6,
                CAR_W - 10,
                CAR_H - 12,
            )

            if player_rect.colliderect(enemy_rect):
                game["game_over"] = True
                if game["score"] > high_score:
                    high_score = game["score"]
                    save_high_score(high_score)
                break

        # Survival points
        game["score"] += 0.06 * dt

    # -------------------- DRAW WORLD --------------------
    draw_road(game["road_offset"])

    # Traffic
    for car in game["traffic"]:
        draw_car(car["x"], car["y"], car["color"])

    # Player
    draw_car(
        game["player_x"],
        game["player_y"],
        CYAN,
        player=True
    )

    # -------------------- HUD --------------------
    draw_panel((16, 16, 165, 80))
    draw_text("SCORE", SMALL, GRAY, 31, 28, center=False)
    draw_text(
        int(game["score"]), BIG, WHITE, 31, 49, center=False
    )

    draw_panel((419, 16, 165, 80))
    draw_text("BEST", SMALL, GRAY, 434, 28, center=False)
    draw_text(
        max(high_score, int(game["score"])),
        BIG, CYAN, 434, 49, center=False
    )

    draw_text(
        f"SPEED  {int(game['speed'] * 20)}",
        SMALL, YELLOW, WIDTH // 2, 29
    )

    # Start screen
    if not game["started"] and not game["game_over"]:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 9, 20, 205))
        screen.blit(overlay, (0, 0))

        draw_text("NEON", TITLE, CYAN, WIDTH // 2, 270)
        draw_text("DRIVE", TITLE, WHITE, WIDTH // 2, 325)

        draw_text(
            "DODGE THE TRAFFIC",
            FONT, GRAY, WIDTH // 2, 385
        )

        draw_panel((100, 430, 400, 125))
        draw_text(
            "LEFT / RIGHT  or  A / D",
            SMALL, WHITE, WIDTH // 2, 461
        )
        draw_text(
            "P  -  PAUSE",
            SMALL, GRAY, WIDTH // 2, 490
        )
        draw_text(
            "PRESS ENTER TO START",
            FONT, YELLOW, WIDTH // 2, 530
        )

    # Pause screen
    if game["paused"] and not game["game_over"]:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 9, 20, 190))
        screen.blit(overlay, (0, 0))

        draw_panel((85, 315, 430, 150))
        draw_text("PAUSED", TITLE, CYAN, WIDTH // 2, 365)
        draw_text(
            "Press P to continue",
            FONT, WHITE, WIDTH // 2, 420
        )

    # Game over screen
    if game["game_over"]:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 9, 20, 205))
        screen.blit(overlay, (0, 0))

        draw_panel((65, 270, 470, 255))
        draw_text(
            "CRASHED!", TITLE, RED, WIDTH // 2, 325
        )
        draw_text(
            f"FINAL SCORE: {int(game['score'])}",
            FONT, WHITE, WIDTH // 2, 390
        )
        draw_text(
            f"BEST SCORE: {high_score}",
            SMALL, CYAN, WIDTH // 2, 425
        )
        draw_text(
            "ENTER  -  RESTART",
            FONT, YELLOW, WIDTH // 2, 470
        )
        draw_text(
            "ESC  -  QUIT",
            SMALL, GRAY, WIDTH // 2, 500
        )

    pygame.display.flip()

pygame.quit()
