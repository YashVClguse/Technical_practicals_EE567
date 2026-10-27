
import pygame
import random
import math
import sys

pygame.init()

# =====================================================
# CONFIGURATION
# =====================================================
WIDTH, HEIGHT = 1100, 650
FPS = 60
WORLD_WIDTH = 4200
GROUND_Y = 550

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("IRON FRONT | Commando Operations")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("consolas", 22, bold=True)
SMALL = pygame.font.SysFont("consolas", 14, bold=True)
MEDIUM = pygame.font.SysFont("consolas", 17, bold=True)
BIG = pygame.font.SysFont("consolas", 46, bold=True)

WHITE = (240, 246, 247)
CYAN = (83, 220, 242)
GREEN = (90, 225, 126)
RED = (245, 76, 75)
GOLD = (255, 201, 66)
DARK = (7, 15, 25)

# =====================================================
# LEVEL
# =====================================================
platforms = [
    pygame.Rect(380, 455, 170, 18),
    pygame.Rect(780, 400, 190, 18),
    pygame.Rect(1190, 455, 200, 18),
    pygame.Rect(1650, 390, 200, 18),
    pygame.Rect(2140, 455, 180, 18),
    pygame.Rect(2600, 405, 210, 18),
    pygame.Rect(3150, 455, 190, 18),
    pygame.Rect(3650, 390, 200, 18),
]

obstacles = [
    pygame.Rect(650, 510, 42, 40),
    pygame.Rect(1070, 505, 55, 45),
    pygame.Rect(1510, 505, 40, 45),
    pygame.Rect(2000, 505, 60, 45),
    pygame.Rect(2470, 505, 45, 45),
    pygame.Rect(2950, 505, 65, 45),
    pygame.Rect(3470, 505, 45, 45),
]

# =====================================================
# UI HELPERS
# =====================================================
def draw_text(text, font, color, position, center=False):
    image = font.render(str(text), True, color)
    shadow = font.render(str(text), True, (0, 0, 0))

    if center:
        rect = image.get_rect(center=position)
    else:
        rect = image.get_rect(topleft=position)

    shadow_rect = rect.copy()
    shadow_rect.x += 2
    shadow_rect.y += 2

    screen.blit(shadow, shadow_rect)
    screen.blit(image, rect)


def draw_panel(rect, border=CYAN, fill=(8, 22, 34)):
    x, y, w, h = rect

    panel = pygame.Surface((w, h), pygame.SRCALPHA)
    panel.fill((*fill, 242))
    screen.blit(panel, (x, y))

    pygame.draw.rect(screen, border, rect, 2, border_radius=10)

    # Decorative corner accents
    pygame.draw.line(screen, WHITE, (x + 10, y + 2),
                     (x + 34, y + 2), 2)
    pygame.draw.line(screen, WHITE, (x + 2, y + 10),
                     (x + 2, y + 28), 2)


def draw_health_bar(x, y, width, height, health):
    pygame.draw.rect(screen, (35, 47, 52),
                     (x, y, width, height), border_radius=5)

    ratio = max(0, min(1, health / 100))
    color = GREEN if health > 30 else RED

    if ratio > 0:
        pygame.draw.rect(
            screen, color,
            (x + 2, y + 2, int((width - 4) * ratio), height - 4),
            border_radius=4
        )

    pygame.draw.rect(screen, (135, 164, 172),
                     (x, y, width, height), 1, border_radius=5)


# =====================================================
# BULLETS
# =====================================================
class Bullet:
    def __init__(self, x, y, direction, enemy=False):
        self.x = float(x)
        self.y = float(y)
        self.direction = direction
        self.speed = 9 if not enemy else 5
        self.enemy = enemy
        self.rect = pygame.Rect(x, y, 15, 5)

    def update(self):
        self.x += self.speed * self.direction
        self.rect.x = int(self.x)

    def draw(self, camera):
        x = self.rect.x - camera
        color = RED if self.enemy else GOLD

        pygame.draw.rect(screen, color,
                         (x, self.rect.y, 15, 5), border_radius=3)
        pygame.draw.circle(screen, WHITE, (x + 12, self.rect.y + 2), 2)

        # Small muzzle-like glow
        pygame.draw.line(screen, color,
                         (x - 5, self.rect.y + 2),
                         (x, self.rect.y + 2), 2)


# =====================================================
# ENEMY
# =====================================================
class Enemy:
    def __init__(self, x):
        self.x = float(x)
        self.spawn_x = x
        self.direction = random.choice([-1, 1])
        self.speed = random.choice([1.0, 1.4, 1.7])
        self.health = 3
        self.alive = True
        self.rect = pygame.Rect(x, GROUND_Y - 48, 32, 48)
        self.shoot_timer = random.randint(65, 130)

    def update(self, player, bullets):
        if not self.alive:
            return

        distance = player.rect.centerx - self.rect.centerx

        if abs(distance) < 330:
            self.direction = 1 if distance > 0 else -1
            self.x += self.speed * self.direction
        else:
            self.x += self.speed * self.direction
            if abs(self.x - self.spawn_x) > 100:
                self.direction *= -1

        self.x = max(0, min(WORLD_WIDTH - 40, self.x))
        self.rect.x = int(self.x)

        self.shoot_timer -= 1

        if abs(distance) < 360 and self.shoot_timer <= 0:
            direction = 1 if distance > 0 else -1

            bullets.append(Bullet(
                self.rect.centerx + direction * 15,
                self.rect.y + 22,
                direction,
                enemy=True
            ))
            self.shoot_timer = 115

    def draw(self, camera):
        if not self.alive:
            return

        x = self.rect.x - camera
        y = self.rect.y

        # Legs
        pygame.draw.rect(screen, (27, 28, 30), (x + 3, y + 35, 10, 13))
        pygame.draw.rect(screen, (27, 28, 30), (x + 19, y + 35, 10, 13))

        # Uniform
        pygame.draw.rect(screen, (156, 55, 49), (x + 4, y + 16, 24, 23))
        pygame.draw.rect(screen, (105, 39, 37), (x + 9, y + 20, 13, 13))

        # Face and helmet
        pygame.draw.circle(screen, (222, 171, 123), (x + 16, y + 10), 10)
        pygame.draw.rect(screen, (83, 40, 38), (x + 4, y + 1, 24, 7))

        # Weapon
        weapon_x = x + 23 if self.direction >= 0 else x - 15
        pygame.draw.rect(screen, (25, 29, 30),
                         (weapon_x, y + 20, 25, 5))

        # Enemy health
        pygame.draw.rect(screen, (25, 25, 25), (x, y - 10, 34, 6))
        pygame.draw.rect(screen, RED,
                         (x + 1, y - 9,
                          int(32 * self.health / 3), 4))


# =====================================================
# COLLECTIBLES
# =====================================================
class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.collected = False
        self.phase = random.random() * 6

    def draw(self, camera):
        if self.collected:
            return

        y = int(self.y + math.sin(
            pygame.time.get_ticks() * 0.004 + self.phase
        ) * 5)

        x = self.x - camera

        pygame.draw.circle(screen, (122, 78, 20), (x, y), 13)
        pygame.draw.circle(screen, GOLD, (x, y), 10)
        pygame.draw.circle(screen, (255, 240, 160), (x - 3, y - 3), 4)
        pygame.draw.circle(screen, (201, 135, 25), (x, y), 6, 2)


# =====================================================
# PLAYER
# =====================================================
class Player:
    def __init__(self):
        self.rect = pygame.Rect(100, GROUND_Y - 52, 32, 52)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.vy = 0.0
        self.speed = 5
        self.facing = 1
        self.health = 100
        self.score = 0
        self.coins = 0
        self.on_ground = False
        self.invincible = 0
        self.shoot_cooldown = 0

    def update(self, keys):
        dx = 0

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -self.speed
            self.facing = -1

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = self.speed
            self.facing = 1

        # Horizontal movement
        self.x = max(0, min(WORLD_WIDTH - self.rect.width,
                            self.x + dx))
        self.rect.x = int(self.x)

        # Horizontal obstacle collision
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle):
                if dx > 0:
                    self.rect.right = obstacle.left
                elif dx < 0:
                    self.rect.left = obstacle.right

                self.x = float(self.rect.x)

        # Vertical physics
        old_bottom = self.rect.bottom
        self.vy = min(self.vy + 0.65, 13)
        self.y += self.vy
        self.rect.y = int(self.y)
        self.on_ground = False

        # Ground collision
        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.y = float(self.rect.y)
            self.vy = 0
            self.on_ground = True

        # Platform collision when descending
        if self.vy >= 0:
            for platform in platforms:
                if (old_bottom <= platform.top + 5
                        and self.rect.colliderect(platform)):
                    self.rect.bottom = platform.top
                    self.y = float(self.rect.y)
                    self.vy = 0
                    self.on_ground = True

        self.invincible = max(0, self.invincible - 1)
        self.shoot_cooldown = max(0, self.shoot_cooldown - 1)

    def jump(self):
        if self.on_ground:
            self.vy = -13
            self.on_ground = False

    def shoot(self, bullets):
        if self.shoot_cooldown == 0:
            bullets.append(Bullet(
                self.rect.centerx + self.facing * 20,
                self.rect.y + 22,
                self.facing
            ))
            self.shoot_cooldown = 13

    def draw(self, camera):
        if self.invincible > 0 and self.invincible % 8 < 4:
            return

        x = self.rect.x - camera
        y = self.rect.y

        # Boots and legs
        pygame.draw.rect(screen, (25, 30, 28), (x + 3, y + 39, 12, 13))
        pygame.draw.rect(screen, (25, 30, 28), (x + 19, y + 39, 12, 13))

        # Uniform and equipment
        pygame.draw.rect(screen, (62, 113, 52), (x + 3, y + 25, 27, 17))
        pygame.draw.rect(screen, (79, 139, 60), (x + 4, y + 13, 25, 24))
        pygame.draw.rect(screen, (47, 81, 41), (x + 8, y + 22, 7, 8))
        pygame.draw.rect(screen, (47, 81, 41), (x + 19, y + 22, 6, 8))

        # Face
        pygame.draw.circle(screen, (224, 177, 132), (x + 17, y + 10), 10)

        # Helmet
        pygame.draw.rect(screen, (44, 81, 42), (x + 4, y, 26, 7))
        pygame.draw.rect(screen, (31, 62, 35), (x + 7, y + 4, 22, 4))

        # Eye
        eye_x = x + 23 if self.facing == 1 else x + 10
        pygame.draw.circle(screen, (20, 25, 24), (eye_x, y + 10), 2)

        # Rifle follows facing direction
        if self.facing == 1:
            weapon = (x + 20, y + 19, 27, 5)
            barrel = (x + 33, y + 17, 15, 2)
        else:
            weapon = (x - 15, y + 19, 27, 5)
            barrel = (x - 16, y + 17, 15, 2)

        pygame.draw.rect(screen, (21, 27, 28), weapon)
        pygame.draw.rect(screen, (137, 152, 148), barrel)


# =====================================================
# BACKGROUND
# =====================================================
def draw_background(camera):
    screen.fill((20, 32, 51))

    # Sunset glow
    pygame.draw.circle(screen, (255, 184, 95), (840, 170), 48)
    pygame.draw.circle(screen, (255, 211, 134), (840, 170), 32)

    # Clouds
    for cx, cy, radius in [
        (150, 145, 42), (190, 130, 48), (235, 150, 38),
        (520, 110, 38), (565, 125, 48), (610, 105, 35)
    ]:
        pygame.draw.circle(screen, (110, 119, 130),
                           (cx - int(camera * 0.05), cy), radius)

    # Distant mountain silhouettes
    offset = int(camera * 0.15) % 300

    for i in range(-1, 7):
        x = i * 300 - offset
        pygame.draw.polygon(screen, (53, 75, 82), [
            (x, GROUND_Y), (x + 150, 220), (x + 310, GROUND_Y)
        ])
        pygame.draw.polygon(screen, (40, 65, 69), [
            (x + 90, GROUND_Y), (x + 240, 285), (x + 390, GROUND_Y)
        ])

    # Jungle trees
    offset = int(camera * 0.35) % 125

    for i in range(-1, 12):
        x = i * 125 - offset
        pygame.draw.rect(screen, (35, 60, 42),
                         (x + 48, 365, 17, 190))
        pygame.draw.circle(screen, (26, 73, 48), (x + 55, 360), 48)
        pygame.draw.circle(screen, (36, 88, 52), (x + 25, 395), 34)
        pygame.draw.circle(screen, (29, 77, 44), (x + 85, 398), 36)

    # Ground
    pygame.draw.rect(screen, (47, 65, 43),
                     (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
    pygame.draw.rect(screen, (111, 151, 70),
                     (0, GROUND_Y, WIDTH, 8))

    for i in range(-1, 30):
        x = i * 50 - int(camera) % 50
        pygame.draw.line(screen, (70, 91, 52),
                         (x, GROUND_Y + 24), (x + 20, GROUND_Y + 24), 2)

    # Platforms
    for p in platforms:
        x = p.x - camera

        if -220 < x < WIDTH + 100:
            pygame.draw.rect(screen, (61, 61, 43),
                             (x, p.y, p.width, p.height))
            pygame.draw.rect(screen, (133, 164, 75),
                             (x, p.y, p.width, 5))

            for k in range(10, p.width, 25):
                pygame.draw.line(screen, (83, 83, 54),
                                 (x + k, p.y + 7),
                                 (x + k - 6, p.y + 17), 2)

            # Grass blades
            for k in range(6, p.width, 15):
                pygame.draw.line(screen, (126, 178, 76),
                                 (x + k, p.y),
                                 (x + k - 2, p.y - 5), 2)

    # Obstacles
    for o in obstacles:
        x = o.x - camera

        if -100 < x < WIDTH + 100:
            pygame.draw.rect(screen, (91, 78, 56),
                             (x, o.y, o.width, o.height))
            pygame.draw.rect(screen, (139, 120, 83),
                             (x + 4, o.y + 4, o.width - 8, 8))

            pygame.draw.line(screen, (47, 47, 36),
                             (x + 4, o.y + 15),
                             (x + o.width - 4, o.y + o.height - 4), 3)

            pygame.draw.line(screen, (47, 47, 36),
                             (x + o.width - 4, o.y + 15),
                             (x + 4, o.y + o.height - 4), 3)


# =====================================================
# HUD
# =====================================================
def draw_hud(player, enemies_left):
    pygame.draw.rect(screen, (5, 12, 23), (0, 0, WIDTH, 100))
    pygame.draw.line(screen, (35, 125, 151),
                     (0, 99), (WIDTH, 99), 2)

    # Player panel
    draw_panel((12, 10, 385, 79))
    draw_text("IRON FRONT", FONT, CYAN, (27, 16))
    draw_text("ELITE COMMANDO", SMALL, (174, 197, 205), (29, 44))
    draw_health_bar(29, 68, 345, 12, player.health)

    # Score panel
    draw_panel((408, 10, 193, 79))
    draw_text("MISSION SCORE", SMALL, (170, 196, 207), (422, 20))
    draw_text(f"{player.score:06d}", FONT, GOLD, (422, 47))

    # Coin panel
    draw_panel((612, 10, 154, 79), border=GOLD)
    draw_text("COLLECTED", SMALL, (170, 196, 207), (625, 20))
    draw_text(f"COINS {player.coins:02d}", MEDIUM, GOLD, (625, 48))

    # Enemy panel
    draw_panel((777, 10, 151, 79), border=RED)
    draw_text("HOSTILES", SMALL, (213, 177, 174), (791, 20))
    draw_text(f"{enemies_left:02d}", FONT, RED, (791, 47))

    # Level panel
    draw_panel((939, 10, 149, 79))
    draw_text("SECTOR", SMALL, (170, 196, 207), (952, 20))
    draw_text("JUNGLE 01", MEDIUM, CYAN, (952, 48))


# =====================================================
# MISSION OVERLAY
# =====================================================
def draw_overlay(title, subtitle, hint):
    shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    shade.fill((2, 7, 15, 215))
    screen.blit(shade, (0, 0))

    border = GREEN if title == "MISSION COMPLETE" else RED
    draw_panel((145, 170, 810, 290), border=border,
               fill=(8, 20, 32))

    draw_text("OPERATION 07  //  JUNGLE OUTPOST",
              SMALL, CYAN, (WIDTH // 2, 207), center=True)

    draw_text(title, BIG, border,
              (WIDTH // 2, 272), center=True)

    draw_text(subtitle, MEDIUM, WHITE,
              (WIDTH // 2, 330), center=True)

    pygame.draw.line(screen, (49, 91, 106),
                     (230, 363), (870, 363), 2)

    draw_text(hint, SMALL, GOLD,
              (WIDTH // 2, 406), center=True)


# =====================================================
# RESET
# =====================================================
def reset_game():
    player = Player()

    enemies = [
        Enemy(x) for x in
        [480, 900, 1320, 1750, 2220, 2700, 3220, 3750]
    ]

    bullets = []
    enemy_bullets = []

    coins = [
        Coin(x, y) for x, y in [
            (250, 490), (440, 410), (710, 490), (850, 355),
            (1100, 480), (1260, 410), (1710, 345), (1900, 490),
            (2190, 410), (2530, 490), (2660, 360), (3060, 490),
            (3240, 410), (3550, 490), (3700, 345), (4020, 490)
        ]
    ]

    return player, enemies, bullets, enemy_bullets, coins


player, enemies, bullets, enemy_bullets, coins = reset_game()
camera = 0
state = "playing"

# =====================================================
# MAIN LOOP
# =====================================================
while True:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            if state != "playing" and event.key in (
                    pygame.K_r, pygame.K_RETURN, pygame.K_SPACE):
                player, enemies, bullets, enemy_bullets, coins = reset_game()
                camera = 0
                state = "playing"

            elif state == "playing" and event.key in (
                    pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                player.jump()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if state == "playing":
                player.shoot(bullets)

    keys = pygame.key.get_pressed()

    if state == "playing":
        player.update(keys)

        # Automatic fire
        if keys[pygame.K_j] or keys[pygame.K_LCTRL]:
            player.shoot(bullets)

        # Follow player with camera
        camera = max(0, min(
            WORLD_WIDTH - WIDTH,
            player.rect.centerx - WIDTH // 2
        ))

        # Player bullets
        for bullet in bullets[:]:
            bullet.update()

            if bullet.x < 0 or bullet.x > WORLD_WIDTH:
                bullets.remove(bullet)
                continue

            for enemy in enemies:
                if enemy.alive and bullet.rect.colliderect(enemy.rect):
                    enemy.health -= 1

                    if enemy.health <= 0:
                        enemy.alive = False
                        player.score += 100

                    if bullet in bullets:
                        bullets.remove(bullet)
                    break

        # Enemy behaviour and contact damage
        for enemy in enemies:
            enemy.update(player, enemy_bullets)

            if enemy.alive and player.rect.colliderect(enemy.rect):
                if player.invincible == 0:
                    player.health -= 15
                    player.invincible = 55

        # Enemy projectiles
        for bullet in enemy_bullets[:]:
            bullet.update()

            if bullet.x < 0 or bullet.x > WORLD_WIDTH:
                enemy_bullets.remove(bullet)
                continue

            if bullet.rect.colliderect(player.rect):
                if player.invincible == 0:
                    player.health -= 10
                    player.invincible = 55

                enemy_bullets.remove(bullet)

        # Collect coins
        for coin in coins:
            coin_rect = pygame.Rect(
                coin.x - 10, coin.y - 10, 20, 20
            )

            if not coin.collected and player.rect.colliderect(coin_rect):
                coin.collected = True
                player.coins += 1
                player.score += 25

        # Win / lose
        if player.health <= 0:
            state = "gameover"

        elif player.rect.right >= WORLD_WIDTH - 40:
            state = "won"

    # =================================================
    # RENDER FRAME
    # =================================================
    draw_background(camera)

    # Finish flag
    finish_x = WORLD_WIDTH - 55 - camera

    pygame.draw.rect(screen, GOLD, (finish_x, 350, 5, 200))
    pygame.draw.polygon(screen, GOLD, [
        (finish_x + 5, 350),
        (finish_x + 58, 365),
        (finish_x + 5, 385)
    ])

    # Objects
    for coin in coins:
        coin.draw(camera)

    for enemy in enemies:
        enemy.draw(camera)

    for bullet in bullets:
        bullet.draw(camera)

    for bullet in enemy_bullets:
        bullet.draw(camera)

    player.draw(camera)

    # UI
    draw_hud(player, sum(enemy.alive for enemy in enemies))

    # Bottom controls
    pygame.draw.rect(screen, (5, 12, 22),
                     (0, HEIGHT - 43, WIDTH, 43))
    pygame.draw.line(screen, (35, 125, 151),
                     (0, HEIGHT - 43), (WIDTH, HEIGHT - 43), 2)

    controls = [
        ("A / D", "MOVE"),
        ("SPACE", "JUMP"),
        ("J / CTRL", "FIRE"),
        ("R / ENTER", "RESTART"),
        ("ESC", "QUIT")
    ]

    cell_width = WIDTH // len(controls)

    for i, (key, action) in enumerate(controls):
        cx = i * cell_width + cell_width // 2

        draw_text(key, SMALL, CYAN, (cx, HEIGHT - 35), center=True)
        draw_text(action, SMALL, WHITE, (cx, HEIGHT - 15), center=True)

        if i:
            pygame.draw.line(
                screen, (39, 65, 76),
                (i * cell_width, HEIGHT - 36),
                (i * cell_width, HEIGHT - 8), 1
            )

    # End screens
    if state == "gameover":
        draw_overlay(
            "MISSION FAILED",
            f"FINAL SCORE: {player.score}  |  COINS: {player.coins}",
            "PRESS R OR ENTER TO DEPLOY AGAIN"
        )

    elif state == "won":
        draw_overlay(
            "MISSION COMPLETE",
            f"FINAL SCORE: {player.score}  |  COINS: {player.coins}",
            "PRESS R OR ENTER TO PLAY AGAIN"
        )

    pygame.display.flip()
