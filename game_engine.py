# Game Engine - Duck behavior, trees, scoring, and layered rendering
# Handles all the game mechanics and scene drawing

import pygame
import random
import time
import math
from enum import Enum


class GameState(Enum):
    """Game states"""
    MENU = 0
    PLAYING = 1
    GAME_OVER = 2
    PAUSED = 3


# ═══════════════════════════════════════════════════════════════════════════
# DUCK  (animated, bobbing, tumble-on-hit)
# ═══════════════════════════════════════════════════════════════════════════

class Duck:
    """Animated duck with flapping wings, vertical bobbing, and tumble death."""

    def __init__(self, screen_width, screen_height, frames):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Animation frames (list of Surfaces)
        self.frames = frames
        self.frame_index = 0
        self.anim_timer = 0
        self.anim_speed = 0.10  # seconds per frame

        self.width = frames[0].get_width()
        self.height = frames[0].get_height()

        # Spawn
        self.spawn()

        # Movement
        self.speed = random.uniform(1.8, 3.5)

        # Vertical bobbing
        self.bob_offset = 0
        self.bob_phase = random.uniform(0, math.pi * 2)
        self.bob_amplitude = random.uniform(6, 14)
        self.bob_speed = random.uniform(2.5, 4.0)

        # State
        self.alive = True
        self.hit = False
        self.hit_time = 0
        self.rotation = 0  # for tumble animation
        self.escaped = False  # True when duck flies off screen without being hit

        # Z-layer (for depth sorting with trees)
        self.z_layer = random.choice([1, 3])  # 1 = behind near trees, 3 = in front

        # Flight pattern
        self.flight_pattern = random.choice(['straight', 'zigzag', 'swoop', 'circular'])
        self.pattern_timer = 0
        self.pattern_phase = random.uniform(0, math.pi * 2)
        # Zigzag params
        self.zigzag_freq = random.uniform(3.0, 6.0)
        self.zigzag_amp = random.uniform(30, 60)
        # Swoop params
        self.swoop_amp = random.uniform(80, 150)
        self.swoop_freq = random.uniform(0.8, 1.5)
        # Circular params
        self.circle_amp_y = random.uniform(40, 80)
        self.circle_freq = random.uniform(1.5, 3.0)

    def spawn(self):
        """Spawn duck at random position"""
        self.y = random.randint(80, 380)
        self.base_y = self.y

        if random.choice([True, False]):
            self.x = -self.width
            self.direction = 1
        else:
            self.x = self.screen_width
            self.direction = -1

    def update(self, dt=1/60):
        """Update duck position and animation"""
        if not self.alive:
            return

        # Animate wing flap
        self.anim_timer += dt
        if self.anim_timer >= self.anim_speed:
            self.anim_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)

        if self.hit:
            # Tumble fall
            fall_elapsed = time.time() - self.hit_time
            self.y += fall_elapsed * 180 * dt * 60
            self.rotation += 8  # spin
            if self.y > self.screen_height + 50:
                self.alive = False
            return

        # Move horizontally
        self.x += self.speed * self.direction

        # Apply flight pattern
        self.pattern_timer += dt
        t = self.pattern_timer

        if self.flight_pattern == 'zigzag':
            # Rapid vertical oscillation
            self.bob_offset = math.sin(t * self.zigzag_freq + self.pattern_phase) * self.zigzag_amp
            self.y = self.base_y + self.bob_offset

        elif self.flight_pattern == 'swoop':
            # Big swooping arc
            self.bob_offset = math.sin(t * self.swoop_freq + self.pattern_phase) * self.swoop_amp
            self.y = self.base_y + self.bob_offset

        elif self.flight_pattern == 'circular':
            # Circular-ish motion
            self.bob_offset = math.sin(t * self.circle_freq + self.pattern_phase) * self.circle_amp_y
            self.y = self.base_y + self.bob_offset
            # Also add horizontal wobble
            self.x += math.cos(t * self.circle_freq + self.pattern_phase) * 1.5

        else:  # straight (with gentle bob)
            self.bob_phase += self.bob_speed * dt
            self.bob_offset = math.sin(self.bob_phase) * self.bob_amplitude
            self.y = self.base_y + self.bob_offset

        # Clamp Y so ducks don't go off-screen vertically
        self.y = max(30, min(self.screen_height - 180, self.y))

        # Remove if off screen horizontally
        if self.x < -self.width - 20 or self.x > self.screen_width + 20:
            self.escaped = True  # mark as escaped for quack
            self.alive = False

    def check_collision(self, aim_x, aim_y, hit_radius=180):
        """Check if shot is close enough to duck"""
        if not self.alive or self.hit:
            return False
        duck_center_x = self.x + self.width // 2
        duck_center_y = self.y + self.height // 2
        distance = ((aim_x - duck_center_x) ** 2 + (aim_y - duck_center_y) ** 2) ** 0.5
        return distance < hit_radius

    def get_center(self):
        return (int(self.x + self.width // 2), int(self.y + self.height // 2))

    def get_hit(self):
        """Mark duck as hit"""
        self.hit = True
        self.hit_time = time.time()
        self.speed = 0

    def draw(self, screen, show_hitbox=False):
        """Draw current animation frame"""
        if not self.alive:
            return

        frame = self.frames[self.frame_index]

        # Flip based on direction
        if self.direction == -1:
            frame = pygame.transform.flip(frame, True, False)

        # Rotate if hit (tumble)
        if self.hit and self.rotation != 0:
            frame = pygame.transform.rotate(frame, self.rotation)

        rect = frame.get_rect(center=(int(self.x + self.width // 2),
                                       int(self.y + self.height // 2)))
        screen.blit(frame, rect)

        # Hit zone (debug)
        if show_hitbox and not self.hit:
            center = self.get_center()
            pygame.draw.circle(screen, (0, 255, 0), center, 180, 1)


# ═══════════════════════════════════════════════════════════════════════════
# TREE  (static obstacle with sway animation)
# ═══════════════════════════════════════════════════════════════════════════

class Tree:
    """Environmental tree that can occlude ducks."""

    def __init__(self, image, x, y, z_layer, scale=1.0):
        if scale != 1.0:
            w = int(image.get_width() * scale)
            h = int(image.get_height() * scale)
            self.image = pygame.transform.smoothscale(image, (w, h))
        else:
            self.image = image

        self.x = x
        self.y = y
        self.z_layer = z_layer  # 0=far bg, 2=mid, 4=foreground

        # Sway animation
        self.sway_phase = random.uniform(0, math.pi * 2)
        self.sway_speed = random.uniform(0.8, 1.5)
        self.sway_amount = random.uniform(1.5, 4.0)
        self.sway_offset = 0

    def update(self, dt=1/60):
        self.sway_phase += self.sway_speed * dt
        self.sway_offset = math.sin(self.sway_phase) * self.sway_amount

    def draw(self, screen):
        screen.blit(self.image, (int(self.x + self.sway_offset), int(self.y)))


# ═══════════════════════════════════════════════════════════════════════════
# PARTICLE  (feathers, hit sparks)
# ═══════════════════════════════════════════════════════════════════════════

class Particle:
    """Small animated particle for hit effects."""

    def __init__(self, x, y, color=None):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-5, -1)
        self.life = 1.0
        self.decay = random.uniform(1.5, 3.0)
        self.size = random.randint(2, 5)
        self.color = color or random.choice([
            (255, 255, 200), (255, 200, 100), (200, 150, 80),
            (255, 100, 50), (255, 255, 255),
        ])

    def update(self, dt=1/60):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.15  # gravity
        self.life -= self.decay * dt
        return self.life > 0

    def draw(self, screen):
        alpha = max(0, min(255, int(self.life * 255)))
        r, g, b = self.color
        pygame.draw.circle(screen, (r, g, b), (int(self.x), int(self.y)), self.size)


# ═══════════════════════════════════════════════════════════════════════════
# FLOATING TEXT  (hit score popups & streak announcements)
# ═══════════════════════════════════════════════════════════════════════════

class FloatingText:
    """Rising, fading text popup for scores and streak announcements."""

    def __init__(self, text, x, y, color=(255, 255, 255), size=36, duration=1.2):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.life = duration
        self.max_life = duration
        self.vy = -1.5  # float upward

    def update(self, dt=1/60):
        self.y += self.vy
        self.life -= dt
        return self.life > 0

    def draw(self, screen, font=None):
        alpha = max(0, min(255, int((self.life / self.max_life) * 255)))
        render_font = pygame.font.Font(None, self.size)
        text_surf = render_font.render(self.text, True, self.color)
        text_surf.set_alpha(alpha)
        rect = text_surf.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(text_surf, rect)


# ═══════════════════════════════════════════════════════════════════════════
# GAME ENGINE
# ═══════════════════════════════════════════════════════════════════════════

class GameEngine:
    """Main game logic controller with layered scene rendering."""

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Game state
        self.state = GameState.PLAYING

        # Scoring
        self.score = 0
        self.ammo = 10
        self.shots_fired = 0
        self.hits = 0
        self.escaped_ducks = 0
        self.consecutive_hits = 0
        self.best_streak = 0
        self.combo_multiplier = 1.0
        self.combo_timer = 0
        self.combo_timeout = 4.0

        # Ducks
        self.ducks = []
        self.max_ducks = 3
        self.last_spawn_time = time.time()
        self.spawn_interval = 2.0

        # Level / difficulty
        self.level = 1
        self.ducks_per_level = 8
        self.ducks_hit_this_level = 0

        # Trees & environment
        self.trees = []
        self.background = None
        self.grass_fg = None

        # Particles
        self.particles = []

        # Floating text popups
        self.floating_texts = []

        # Streak tracking
        self.streak_names = {
            2: 'DOUBLE KILL!',
            3: 'TRIPLE KILL!',
            4: 'MEGA KILL!',
            5: 'ULTRA KILL!!',
        }

        # Quack sound (set externally via load_quack_sound)
        self.quack_sound = None

        # Effects
        self.shot_flash = False
        self.flash_time = 0
        self.flash_duration = 0.1
        self.recoil_offset = (0, 0)
        self.recoil_active = False
        self.recoil_time = 0

        # Slow motion
        self.slow_motion = False
        self.slow_motion_time = 0

    def load_quack_sound(self, sound):
        """Set the quack sound effect."""
        self.quack_sound = sound

    def load_duck_frames(self, frames):
        """Load list of duck animation frame surfaces."""
        self.duck_frames = frames

    def load_duck_image(self, duck_image):
        """Legacy compat — wrap single image into 1-frame list."""
        self.duck_frames = [duck_image]

    def load_scene(self, background, tree_images, grass_fg=None):
        """Set up trees and environment."""
        self.background = background
        self.grass_fg = grass_fg

        # Place trees at various positions and depths
        tree_configs = [
            # (image_idx, x, y, z_layer, scale)
            (0, 50,  340, 0, 0.7),    # far pine left
            (1, 350, 310, 0, 0.6),    # far oak
            (0, 750, 330, 0, 0.65),   # far pine right
            (2, 1100, 360, 0, 0.55),  # far bush

            (1, 150, 350, 2, 0.9),    # mid oak
            (0, 550, 330, 2, 0.85),   # mid pine
            (2, 900, 370, 2, 0.8),    # mid bush

            (0, 30,  380, 4, 1.1),    # near pine left
            (1, 400, 350, 4, 1.0),    # near oak
            (2, 700, 400, 4, 1.05),   # near bush
            (0, 1050, 370, 4, 1.15),  # near pine right
        ]

        for img_idx, x, y, z, scale in tree_configs:
            if img_idx < len(tree_images):
                self.trees.append(Tree(tree_images[img_idx], x, y, z, scale))

    def spawn_duck(self):
        """Spawn a new animated duck"""
        if len(self.ducks) < self.max_ducks:
            new_duck = Duck(self.screen_width, self.screen_height, self.duck_frames)
            # Scale speed with level
            new_duck.speed *= (1 + (self.level - 1) * 0.12)
            self.ducks.append(new_duck)
            self.last_spawn_time = time.time()
            # Quack on spawn
            if self.quack_sound:
                self.quack_sound.play()

    def toggle_pause(self):
        """Toggle between PLAYING and PAUSED."""
        if self.state == GameState.PLAYING:
            self.state = GameState.PAUSED
        elif self.state == GameState.PAUSED:
            self.state = GameState.PLAYING

    def update(self):
        """Update game state"""
        if self.state != GameState.PLAYING:
            return

        dt = 1 / 60  # fixed timestep approx

        # Update ducks
        for duck in self.ducks[:]:
            duck.update(dt)
            if not duck.alive:
                if duck.escaped:
                    self.escaped_ducks += 1
                # Quack when duck escapes
                if duck.escaped and self.quack_sound:
                    self.quack_sound.play()
                self.ducks.remove(duck)

        # Update trees (sway)
        for tree in self.trees:
            tree.update(dt)

        # Update particles
        self.particles = [p for p in self.particles if p.update(dt)]

        # Update floating texts
        self.floating_texts = [ft for ft in self.floating_texts if ft.update(dt)]

        # Spawn new ducks
        if time.time() - self.last_spawn_time > self.spawn_interval:
            self.spawn_duck()

        # Update effects
        if self.shot_flash and time.time() - self.flash_time > self.flash_duration:
            self.shot_flash = False

        if self.recoil_active and time.time() - self.recoil_time > 0.15:
            self.recoil_active = False
            self.recoil_offset = (0, 0)

        if self.slow_motion and time.time() - self.slow_motion_time > 0.5:
            self.slow_motion = False

        # Combo timeout - reset combo if no hit for a while
        if self.consecutive_hits > 0:
            self.combo_timer += dt
            if self.combo_timer > self.combo_timeout:
                self.consecutive_hits = 0
                self.combo_multiplier = 1.0
                self.combo_timer = 0

        # Check game over
        if self.ammo <= 0:
            self.state = GameState.GAME_OVER

    def shoot(self, aim_x, aim_y):
        """Fire a shot at aim position. Returns True if hit a duck."""
        if self.ammo <= 0:
            return False

        self.ammo -= 1
        self.shots_fired += 1

        # Visual effects
        self.shot_flash = True
        self.flash_time = time.time()
        self.recoil_active = True
        self.recoil_time = time.time()
        self.recoil_offset = (random.randint(-5, 5), random.randint(-5, 5))

        # Check hit on any duck
        hit_duck = None
        for duck in self.ducks:
            if duck.check_collision(aim_x, aim_y):
                hit_duck = duck
                break

        if hit_duck:
            hit_duck.get_hit()
            self.hits += 1
            self.consecutive_hits += 1
            self.combo_timer = 0
            if self.consecutive_hits > self.best_streak:
                self.best_streak = self.consecutive_hits

            # Spawn feather particles
            cx, cy = hit_duck.get_center()
            for _ in range(12):
                self.particles.append(Particle(cx, cy))

            # Combo multiplier
            if self.consecutive_hits >= 5:
                self.combo_multiplier = 2.0
            elif self.consecutive_hits >= 3:
                self.combo_multiplier = 1.5
            else:
                self.combo_multiplier = 1.0

            points = int(100 * self.combo_multiplier)
            self.score += points

            # Track ducks hit for level progression
            self.ducks_hit_this_level += 1
            if self.ducks_hit_this_level >= self.ducks_per_level:
                self._advance_level()

            # Floating score text at hit position
            score_color = (255, 215, 0) if self.combo_multiplier > 1 else (255, 255, 255)
            self.floating_texts.append(
                FloatingText(f"+{points}", cx, cy - 20, color=score_color)
            )

            # Streak announcement
            if self.consecutive_hits in self.streak_names:
                streak_text = self.streak_names[self.consecutive_hits]
                self.floating_texts.append(
                    FloatingText(
                        streak_text,
                        self.screen_width // 2,
                        self.screen_height // 3,
                        color=(255, 50, 50),
                        size=64,
                        duration=1.8,
                    )
                )
            elif self.consecutive_hits > 5:
                self.floating_texts.append(
                    FloatingText(
                        f"{self.consecutive_hits}x STREAK!",
                        self.screen_width // 2,
                        self.screen_height // 3,
                        color=(255, 0, 255),
                        size=72,
                        duration=2.0,
                    )
                )

            # Perfect shot check
            duck_center_x = hit_duck.x + hit_duck.width // 2
            duck_center_y = hit_duck.y + hit_duck.height // 2
            distance = ((aim_x - duck_center_x) ** 2 + (aim_y - duck_center_y) ** 2) ** 0.5

            if distance < 15:
                self.slow_motion = True
                self.slow_motion_time = time.time()

            return True
        else:
            self.consecutive_hits = 0
            self.combo_multiplier = 1.0
            self.combo_timer = 0
            return False

    def _advance_level(self):
        """Increase difficulty when enough ducks have been hit."""
        self.level += 1
        self.ducks_hit_this_level = 0
        self.ammo = min(self.ammo + 5, 20)  # bonus ammo on level up

        # Scale difficulty
        self.max_ducks = min(3 + self.level, 8)
        self.spawn_interval = max(2.0 - self.level * 0.15, 0.8)

        # Announce
        self.floating_texts.append(
            FloatingText(
                f"LEVEL {self.level}!",
                self.screen_width // 2,
                self.screen_height // 3,
                color=(0, 255, 200),
                size=72,
                duration=2.0,
            )
        )
        self.floating_texts.append(
            FloatingText(
                f"+5 AMMO BONUS",
                self.screen_width // 2,
                self.screen_height // 3 + 60,
                color=(255, 215, 0),
                size=40,
                duration=1.5,
            )
        )

    def get_accuracy(self):
        if self.shots_fired == 0:
            return 0.0
        return (self.hits / self.shots_fired) * 100

    # ─── LAYERED SCENE RENDERING ─────────────────────────────────────────

    def draw_scene(self, screen, show_hitbox=False, offset=(0, 0)):
        """
        Draw the entire scene in correct z-order:
          Layer 0: far trees
          Layer 1: some ducks (behind near trees)
          Layer 2: mid trees
          Layer 3: some ducks (in front of everything)
          Layer 4: near/foreground trees
          Layer 5: grass overlay
        """
        ox, oy = offset

        # Background
        if self.background:
            screen.blit(self.background, (ox, oy))

        # Collect all drawables with their z_layer
        drawables = []

        for tree in self.trees:
            drawables.append((tree.z_layer, 'tree', tree))

        for duck in self.ducks:
            drawables.append((duck.z_layer, 'duck', duck))

        # Sort by z_layer (lower = further back)
        drawables.sort(key=lambda d: d[0])

        # Draw everything in order
        for z, kind, obj in drawables:
            if kind == 'tree':
                obj.draw(screen)
            elif kind == 'duck':
                obj.draw(screen, show_hitbox=show_hitbox)

        # Particles (always on top of scene)
        for p in self.particles:
            p.draw(screen)

        # Floating texts (on top of scene)
        for ft in self.floating_texts:
            ft.draw(screen, None)  # uses its own font

        # Foreground grass (on top of everything except UI)
        if self.grass_fg:
            screen.blit(self.grass_fg, (0, self.screen_height - self.grass_fg.get_height()))

    def draw_ui(self, screen, font):
        """Draw game UI elements"""

        # Semi-transparent HUD background
        hud_bg = pygame.Surface((250, 185), pygame.SRCALPHA)
        hud_bg.fill((0, 0, 0, 100))
        screen.blit(hud_bg, (10, 10))

        # Score
        score_text = font.render(f"SCORE: {self.score}", True, (255, 255, 255))
        screen.blit(score_text, (20, 20))

        # Ammo with flash warning when low
        if self.ammo <= 3:
            flash = int(time.time() * 4) % 2 == 0
            ammo_color = (255, 80, 80) if flash else (255, 255, 255)
        else:
            ammo_color = (255, 255, 255)
        ammo_text = font.render(f"AMMO: {self.ammo}", True, ammo_color)
        screen.blit(ammo_text, (20, 55))

        # Accuracy
        accuracy_text = font.render(f"ACCURACY: {self.get_accuracy():.1f}%", True, (255, 255, 255))
        screen.blit(accuracy_text, (20, 90))

        # Escaped ducks
        escaped_text = font.render(f"ESCAPED: {self.escaped_ducks}", True, (255, 150, 100))
        screen.blit(escaped_text, (20, 125))

        # Combo multiplier
        if self.combo_multiplier > 1.0:
            combo_text = font.render(f"COMBO x{self.combo_multiplier:.1f}", True, (255, 215, 0))
            screen.blit(combo_text, (20, 160))

        # Level
        level_text = font.render(f"LEVEL: {self.level}", True, (0, 255, 200))
        screen.blit(level_text, (20, 195))

        # Best streak
        if self.best_streak >= 2:
            streak_text = font.render(f"BEST STREAK: {self.best_streak}", True, (255, 100, 255))
            screen.blit(streak_text, (20, 230))

    def draw_effects(self, screen, crosshair_pos):
        """Draw visual effects"""
        if self.shot_flash:
            # Muzzle flash ring
            pygame.draw.circle(screen, (255, 255, 200), crosshair_pos, 35, 4)
            pygame.draw.circle(screen, (255, 200, 100), crosshair_pos, 25, 2)

    def draw_pause_overlay(self, screen):
        """Draw pause menu overlay with current stats."""
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        # PAUSED title
        title_font = pygame.font.Font(None, 96)
        title = title_font.render("PAUSED", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 120))
        screen.blit(title, title_rect)

        # Current stats
        stat_font = pygame.font.Font(None, 36)
        stats = [
            f"Score: {self.score}  |  Level: {self.level}",
            f"Accuracy: {self.get_accuracy():.1f}%  |  Best Streak: {self.best_streak}",
            f"Ammo: {self.ammo}  |  Ducks Hit: {self.hits}  |  Escaped: {self.escaped_ducks}",
        ]
        for i, line in enumerate(stats):
            text = stat_font.render(line, True, (180, 220, 255))
            rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 40 + i * 35))
            screen.blit(text, rect)

        # Instructions
        hint_font = pygame.font.Font(None, 36)
        hints = [
            "Press P to Resume",
            "Press M to Mute/Unmute Music",
            "Press \u2191\u2193 to Adjust Volume",
            "Press ESC to Quit",
        ]
        for i, hint in enumerate(hints):
            text = hint_font.render(hint, True, (200, 200, 200))
            rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 100 + i * 35))
            screen.blit(text, rect)

    def reset(self):
        """Reset game to initial state"""
        self.state = GameState.PLAYING
        self.score = 0
        self.ammo = 10
        self.shots_fired = 0
        self.hits = 0
        self.escaped_ducks = 0
        self.consecutive_hits = 0
        self.best_streak = 0
        self.combo_multiplier = 1.0
        self.combo_timer = 0
        self.level = 1
        self.ducks_hit_this_level = 0
        self.max_ducks = 3
        self.spawn_interval = 2.0
        self.ducks.clear()
        self.particles.clear()
        self.floating_texts.clear()
        self.last_spawn_time = time.time()
