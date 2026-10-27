
import pygame
import random
import math
import sys

pygame.init()

# ---------------- CONFIGURATION ----------------
WIDTH, HEIGHT = 1000, 700
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NEBULA STRIKE | Space Shooter")
clock = pygame.time.Clock()

# Colors
BG = (4, 7, 23)
WHITE = (240, 248, 255)
CYAN = (30, 220, 255)
BLUE = (35, 100, 255)
PURPLE = (150, 65, 255)
RED = (255, 65, 95)
ORANGE = (255, 155, 45)
GREEN = (50, 255, 150)
MUTED = (115, 145, 185)

FONT = pygame.font.SysFont("consolas", 19, bold=True)
SMALL = pygame.font.SysFont("consolas", 14)
TITLE = pygame.font.SysFont("consolas", 53, bold=True)
SUBTITLE = pygame.font.SysFont("consolas", 25, bold=True)

MENU, PLAYING, GAME_OVER = 0, 1, 2

# ---------------- GRAPHICS HELPERS ----------------
def text(surface, message, font, color, pos, center=True):
    image = font.render(str(message), True, color)
    rect = image.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    surface.blit(image, rect)


def glow(surface, pos, radius, color):
    """Draw a soft neon glow."""
    layer = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
    cx = cy = radius * 2

    for r in range(radius * 2, 1, -3):
        alpha = max(1, int(12 * (1 - r / (radius * 2))))
        pygame.draw.circle(
            layer, (*color, alpha), (cx, cy), r
        )

    surface.blit(layer, (pos[0] - cx, pos[1] - cy))


def neon_panel(rect, color=CYAN, fill=(7, 14, 35)):
    pygame.draw.rect(screen, fill, rect, border_radius=12)
    pygame.draw.rect(screen, (*color,), rect, 1, border_radius=12)


def button(label, rect, mouse, selected=False):
    hover = rect.collidepoint(mouse)
    color = CYAN if hover or selected else BLUE

    pygame.draw.rect(
        screen, (8, 25, 60) if not hover else (10, 50, 90),
        rect, border_radius=9
    )
    pygame.draw.rect(screen, color, rect, 2, border_radius=9)

    if hover:
        glow(screen, rect.center, 20, CYAN)

    text(screen, label, FONT, WHITE, rect.center)
    return hover


# ---------------- BACKGROUND ----------------
stars = [
    [random.randrange(WIDTH), random.randrange(HEIGHT),
     random.choice([1, 1, 2, 2, 3])]
    for _ in range(125)
]


def draw_background():
    screen.fill(BG)

    # Subtle nebula-like light
    for x, y, radius, color in [
        (150, 220, 170, (18, 15, 65)),
        (800, 400, 220, (10, 35, 75)),
        (500, 120, 130, (30, 10, 60)),
    ]:
        glow(screen, (x, y), radius // 2, color)

    # Moving stars
    for star in stars:
        x, y, size = star
        pygame.draw.circle(screen, (75, 125, 190), (x, y), size)
        star[1] += size

        if star[1] >= HEIGHT:
            star[0] = random.randrange(WIDTH)
            star[1] = 0

    # Futuristic grid near the bottom
    for y in range(HEIGHT - 100, HEIGHT, 25):
        pygame.draw.line(screen, (12, 30, 62), (0, y), (WIDTH, y))

    for x in range(0, WIDTH, 60):
        pygame.draw.line(
            screen, (10, 24, 48),
            (x, HEIGHT - 100), (x, HEIGHT)
        )


# ---------------- SPACESHIP GRAPHICS ----------------
def draw_player(rect):
    x, y = rect.centerx, rect.centery

    # Engine flame
    flame = random.randint(12, 23)
    pygame.draw.polygon(
        screen, BLUE,
        [(x - 9, rect.bottom - 7),
         (x, rect.bottom + flame),
         (x + 9, rect.bottom - 7)]
    )
    pygame.draw.polygon(
        screen, CYAN,
        [(x - 4, rect.bottom - 4),
         (x, rect.bottom + flame // 2),
         (x + 4, rect.bottom - 4)]
    )

    # Wings and hull
    pygame.draw.polygon(
        screen, BLUE,
        [(x, rect.top), (rect.left, rect.bottom - 3),
         (x - 3, y + 5), (x, y + 12),
         (x + 3, y + 5), (rect.right, rect.bottom - 3)]
    )

    pygame.draw.polygon(
        screen, CYAN,
        [(x, rect.top + 4), (x - 10, rect.bottom - 8),
         (x, rect.bottom - 16), (x + 10, rect.bottom - 8)]
    )

    pygame.draw.ellipse(
        screen, WHITE, (x - 4, y - 7, 8, 18)
    )

    pygame.draw.line(
        screen, CYAN, (x - 12, y + 12),
        (x - 19, rect.bottom - 5), 2
    )
    pygame.draw.line(
        screen, CYAN, (x + 12, y + 12),
        (x + 19, rect.bottom - 5), 2
    )


def draw_enemy(rect, kind=0):
    x, y = rect.center

    color = RED if kind != 2 else PURPLE

    glow(screen, (x, y), 14, color)

    pygame.draw.polygon(
        screen, color,
        [(rect.left, rect.top + 5),
         (x, rect.bottom),
         (rect.right, rect.top + 5),
         (x + 6, rect.top),
         (x, rect.top + 8),
         (x - 6, rect.top)]
    )

    pygame.draw.polygon(
        screen, (80, 20, 55),
        [(x - 5, rect.top + 7), (x, y + 3),
         (x + 5, rect.top + 7)]
    )

    pygame.draw.circle(screen, ORANGE, (x, y), 3)


# ---------------- GAME LOGIC ----------------
def new_game():
    return {
        "player": pygame.Rect(WIDTH // 2 - 20, HEIGHT - 105, 40, 48),
        "health": 100,
        "score": 0,
        "bullets": [],
        "enemy_bullets": [],
        "enemies": [],
        "particles": [],
        "last_shot": 0,
        "last_spawn": 0,
        "level": 1,
        "invulnerable": 0,
    }


def explode(game, x, y, color):
    for _ in range(16):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(1.5, 5)

        game["particles"].append({
            "x": float(x),
            "y": float(y),
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,
            "life": random.randint(15, 35),
            "color": color,
        })


def draw_hud(game):
    # Top HUD
    neon_panel((18, 16, WIDTH - 36, 78), CYAN, (5, 12, 31))

    text(screen, "NEBULA STRIKE", SMALL, CYAN, (38, 31), False)
    text(screen, f"SCORE  {game['score']:05d}",
         FONT, WHITE, (WIDTH // 2, 43))

    text(screen, f"LEVEL {game['level']}",
         FONT, ORANGE, (WIDTH - 145, 43))

    # Health bar
    text(screen, "HULL", SMALL, WHITE, (38, 61), False)
    pygame.draw.rect(screen, (40, 48, 75), (95, 62, 180, 14), border_radius=5)

    health_width = int(176 * max(0, game["health"]) / 100)
    if health_width:
        color = GREEN if game["health"] > 35 else RED
        pygame.draw.rect(
            screen, color, (97, 64, health_width, 10), border_radius=4
        )

    text(screen, f"{max(0, game['health'])}%",
         SMALL, WHITE, (290, 61), False)


# ---------------- MAIN GAME ----------------
def main():
    state = MENU
    game = new_game()
    running = True

    play_button = pygame.Rect(WIDTH // 2 - 115, 380, 230, 54)
    restart_button = pygame.Rect(WIDTH // 2 - 115, 420, 230, 54)
    menu_button = pygame.Rect(WIDTH // 2 - 115, 490, 230, 48)

    while running:
        clock.tick(FPS)
        now = pygame.time.get_ticks()
        mouse = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if state == PLAYING:
                        state = MENU
                    else:
                        running = False

                if state == MENU and event.key in (
                    pygame.K_RETURN, pygame.K_SPACE
                ):
                    game = new_game()
                    state = PLAYING

                elif state == GAME_OVER and event.key in (
                    pygame.K_RETURN, pygame.K_r, pygame.K_SPACE
                ):
                    game = new_game()
                    state = PLAYING

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if state == MENU and play_button.collidepoint(event.pos):
                    game = new_game()
                    state = PLAYING

                elif state == GAME_OVER:
                    if restart_button.collidepoint(event.pos):
                        game = new_game()
                        state = PLAYING
                    elif menu_button.collidepoint(event.pos):
                        state = MENU

        draw_background()

        # -------- MAIN MENU --------
        if state == MENU:
            glow(screen, (WIDTH // 2, 205), 90, BLUE)

            text(screen, "NEBULA", TITLE, WHITE, (WIDTH // 2, 185))
            text(screen, "S T R I K E", SUBTITLE, CYAN,
                 (WIDTH // 2, 244))

            text(screen, "DEFEND THE GALAXY",
                 SMALL, MUTED, (WIDTH // 2, 290))

            # Decorative ship
            ship = pygame.Rect(WIDTH // 2 - 20, 310, 40, 48)
            draw_player(ship)

            button("▶   START MISSION", play_button, mouse)

            text(screen, "CONTROLS", SMALL, CYAN,
                 (WIDTH // 2, 480))
            text(screen, "WASD / ARROWS  -  MOVE",
                 SMALL, WHITE, (WIDTH // 2, 510))
            text(screen, "SPACE  -  FIRE WEAPONS",
                 SMALL, WHITE, (WIDTH // 2, 535))
            text(screen, "ESC  -  BACK TO MENU / EXIT",
                 SMALL, MUTED, (WIDTH // 2, 560))

            text(screen, "PYTHON + PYGAME",
                 SMALL, (65, 95, 140), (WIDTH // 2, 660))

        # -------- GAMEPLAY --------
        elif state == PLAYING:
            player = game["player"]
            keys = pygame.key.get_pressed()

            dx = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - \
                 int(keys[pygame.K_LEFT] or keys[pygame.K_a])
            dy = int(keys[pygame.K_DOWN] or keys[pygame.K_s]) - \
                 int(keys[pygame.K_UP] or keys[pygame.K_w])

            # Normalize diagonal movement
            length = math.hypot(dx, dy)
            if length:
                player.x += int(dx / length * 5)
                player.y += int(dy / length * 5)

            player.clamp_ip(pygame.Rect(8, 100, WIDTH - 16, HEIGHT - 110))

            # Shoot with cooldown
            if keys[pygame.K_SPACE] and now - game["last_shot"] > 190:
                game["bullets"].append(
                    pygame.Rect(player.centerx - 3, player.top - 14, 6, 18)
                )
                game["last_shot"] = now

            # Difficulty progression
            game["level"] = 1 + game["score"] // 150
            spawn_delay = max(260, 800 - game["level"] * 65)

            if now - game["last_spawn"] > spawn_delay:
                size = random.choice([30, 34, 40])
                enemy = pygame.Rect(
                    random.randint(20, WIDTH - size - 20),
                    90, size, size
                )

                game["enemies"].append({
                    "rect": enemy,
                    "speed": random.uniform(1.3, 2.3)
                             + min(game["level"] * 0.25, 3),
                    "kind": random.choice([0, 1, 2]),
                    "last_shot": now,
                    "phase": random.random() * math.tau,
                })
                game["last_spawn"] = now

            # Player bullets
            for bullet in game["bullets"][:]:
                bullet.y -= 10
                if bullet.bottom < 90:
                    game["bullets"].remove(bullet)

            # Enemies and enemy projectiles
            for enemy in game["enemies"][:]:
                rect = enemy["rect"]
                rect.y += int(enemy["speed"])
                rect.x += int(math.sin(now / 450 + enemy["phase"]) * 1.5)

                if now - enemy["last_shot"] > 1900 and rect.top > 95:
                    game["enemy_bullets"].append(
                        pygame.Rect(rect.centerx - 3, rect.bottom, 6, 13)
                    )
                    enemy["last_shot"] = now

                if rect.top > HEIGHT:
                    game["enemies"].remove(enemy)
                    game["health"] -= 10

                elif rect.colliderect(player):
                    game["enemies"].remove(enemy)
                    explode(game, rect.centerx, rect.centery, RED)
                    game["health"] -= 20

            for bullet in game["enemy_bullets"][:]:
                bullet.y += 5

                if bullet.top > HEIGHT:
                    game["enemy_bullets"].remove(bullet)

                elif bullet.colliderect(player):
                    game["enemy_bullets"].remove(bullet)
                    if now > game["invulnerable"]:
                        game["health"] -= 10
                        game["invulnerable"] = now + 350
                        explode(
                            game, player.centerx, player.centery, ORANGE
                        )

            # Player bullet / enemy collisions
            for bullet in game["bullets"][:]:
                for enemy in game["enemies"][:]:
                    if bullet.colliderect(enemy["rect"]):
                        if bullet in game["bullets"]:
                            game["bullets"].remove(bullet)

                        game["enemies"].remove(enemy)
                        game["score"] += 10

                        explode(
                            game, enemy["rect"].centerx,
                            enemy["rect"].centery, CYAN
                        )
                        break

            # Update explosion particles
            for particle in game["particles"][:]:
                particle["x"] += particle["vx"]
                particle["y"] += particle["vy"]
                particle["life"] -= 1

                if particle["life"] <= 0:
                    game["particles"].remove(particle)
                else:
                    pygame.draw.circle(
                        screen, particle["color"],
                        (int(particle["x"]), int(particle["y"])),
                        max(1, particle["life"] // 10)
                    )

            # Draw bullets with neon effects
            for bullet in game["bullets"]:
                glow(screen, bullet.center, 9, CYAN)
                pygame.draw.rect(screen, WHITE, bullet, border_radius=3)

            for bullet in game["enemy_bullets"]:
                glow(screen, bullet.center, 8, RED)
                pygame.draw.rect(screen, RED, bullet, border_radius=3)

            # Draw enemies
            for enemy in game["enemies"]:
                draw_enemy(enemy["rect"], enemy["kind"])

            # Flash player briefly after taking damage
            if now > game["invulnerable"] or now % 120 < 60:
                draw_player(player)

            draw_hud(game)

            text(screen, "SPACE: FIRE", SMALL, MUTED,
                 (WIDTH - 135, HEIGHT - 26))

            if game["health"] <= 0:
                game["health"] = 0
                state = GAME_OVER

        # -------- GAME OVER --------
        elif state == GAME_OVER:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((2, 4, 18, 205))
            screen.blit(overlay, (0, 0))

            neon_panel((WIDTH // 2 - 225, 210, 450, 340), RED, (8, 10, 30))

            glow(screen, (WIDTH // 2, 280), 55, RED)

            text(screen, "MISSION FAILED", TITLE, RED,
                 (WIDTH // 2, 280))
            text(screen, "YOUR SHIP HAS BEEN DESTROYED",
                 SMALL, MUTED, (WIDTH // 2, 330))

            text(screen, "FINAL SCORE", SMALL, CYAN,
                 (WIDTH // 2, 375))
            text(screen, f"{game['score']:05d}",
                 TITLE, WHITE, (WIDTH // 2, 410))

            button("↻   PLAY AGAIN", restart_button, mouse)
            button("MAIN MENU", menu_button, mouse)

            text(screen, "ENTER / R TO RESTART   •   ESC TO EXIT",
                 SMALL, MUTED, (WIDTH // 2, 585))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
