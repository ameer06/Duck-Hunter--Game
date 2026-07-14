# Duck Hunter Game - Gesture Controlled!
# Made by: Mohamed
# Uses hand tracking to shoot ducks (like the classic Duck Hunt)

import pygame
import cv2
import random
import time
from hand_gesture import HandGestureDetector
from game_engine import GameEngine, GameState
from highscore import add_score, get_high_score, get_scores


class FingerGunDuckHunter:
    """Main game class — manages window, input, camera, and game loop."""
    
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.init()
        pygame.mixer.init()
        
        # game window setup
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Finger Gun Duck Hunter")
        
        self.clock = pygame.time.Clock()
        self.FPS = 60  # runs smooth at 60fps
        
        # fonts for UI text
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 72)
        self.hint_font = pygame.font.Font(None, 24)
        self.warn_font = pygame.font.Font(None, 40)
        self.vol_font = pygame.font.Font(None, 36)
        
        self.load_assets()
        
        # setup webcam
        self.camera_index = 0
        self.camera = None
        self._init_camera(self.camera_index)
        
        # hand tracking stuff
        self.gesture_detector = HandGestureDetector()
        
        # game logic handler
        self.game_engine = GameEngine(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.game_engine.state = GameState.MENU
        self.game_engine.load_duck_frames(self.duck_frames)
        self.game_engine.load_scene(self.background, self.tree_images, self.grass_fg)

        # Load quack sound into engine
        try:
            quack = pygame.mixer.Sound('assets/quack.wav')
            quack.set_volume(0.5)
            self.game_engine.load_quack_sound(quack)
            print("✓ Quack sound loaded")
        except Exception as e:
            print(f"Warning: Could not load quack sound: {e}")
        
        self.running = True
        self.show_webcam = True  # press W to toggle
        self.show_fps = True
        self.show_hitbox = False  # press H to toggle
        self._game_over_scored = False
        self._music_faded_out = False
        self._quit_confirm = False  # quit confirmation state on menu

        # Volume control
        self.music_volume = 0.45
        self._volume_timer = 0  # shows volume indicator briefly

        # Screen shake
        self.shake_offset = [0, 0]
        self.shake_intensity = 0
        self.shake_decay = 0.85

        # Cached overlay surfaces (created once, reused every frame)
        self._full_overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self._full_overlay.set_alpha(200)
        self._full_overlay.fill((0, 0, 0))
        self._menu_overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self._menu_overlay.set_alpha(160)
        self._menu_overlay.fill((0, 0, 0))
        self._vol_bg = pygame.Surface((300, 40), pygame.SRCALPHA)
        self._vol_bg.fill((0, 0, 0, 150))
        
    def load_assets(self):
        """Load game assets – sounds and visuals loaded independently"""
        # ── Sounds ─────────────────────────────────────────────────────────
        try:
            self.gunshot_sound = pygame.mixer.Sound('assets/gunshot.wav')
            self.gunshot_sound.set_volume(0.85)
            print("✓ Gunshot sound loaded")
        except Exception as e:
            print(f"Warning: no gunshot sound ({e})")
            self.gunshot_sound = None

        try:
            pygame.mixer.music.load('assets/bg_music.wav')
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1)
            self.music_muted = False
            print("✓ Background music started")
        except Exception as e:
            print(f"Warning: no background music ({e})")
            self.music_muted = True

        # ── Duck sprite sheet (4-frame animation) ─────────────────────────
        FRAME_W, FRAME_H = 120, 100
        try:
            sheet = pygame.image.load('assets/duck_sheet.png').convert_alpha()
            num_frames = sheet.get_width() // FRAME_W
            self.duck_frames = []
            for i in range(num_frames):
                frame = sheet.subsurface((i * FRAME_W, 0, FRAME_W, FRAME_H))
                self.duck_frames.append(frame.copy())
            print(f"✓ Duck sprite sheet loaded ({num_frames} frames)")
        except Exception as e:
            print(f"Warning: no sprite sheet ({e}) – using fallback")
            self.duck_frames = [self._make_fallback_duck()]

        # ── Background ────────────────────────────────────────────────────
        try:
            self.background = pygame.image.load('assets/background.png').convert()
            self.background = pygame.transform.scale(
                self.background, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            print("✓ Background loaded")
        except Exception:
            self.background = self._make_fallback_background()

        # ── Trees ─────────────────────────────────────────────────────────
        self.tree_images = []
        for name in ['assets/tree1.png', 'assets/tree2.png', 'assets/tree3.png']:
            try:
                img = pygame.image.load(name).convert_alpha()
                self.tree_images.append(img)
            except Exception:
                pass
        if self.tree_images:
            print(f"✓ {len(self.tree_images)} tree sprites loaded")

        # ── Foreground grass ──────────────────────────────────────────────
        try:
            self.grass_fg = pygame.image.load('assets/grass_fg.png').convert_alpha()
            print("✓ Foreground grass loaded")
        except Exception:
            self.grass_fg = None

        # ── Crosshair ─────────────────────────────────────────────────────
        try:
            self.crosshair = pygame.image.load('assets/crosshair.png').convert_alpha()
            print("✓ Crosshair loaded")
        except Exception:
            self.crosshair = self._make_fallback_crosshair()

    def _init_camera(self, index):
        """Initialize camera at specific index"""
        if self.camera:
            self.camera.release()
            
        print(f"Opening camera index {index}...")
        try:
            self.camera = cv2.VideoCapture(index)
        except Exception as e:
            print(f"Failed to create camera: {e}")
            self.camera = None
            return False
        
        if self.camera is None or not self.camera.isOpened():
            print(f"Failed to open camera index {index}")
            self.camera = None
            return False
            
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        print(f"Camera {index} opened successfully")
        return True

    def cycle_camera(self):
        """Try next camera index (0-3)"""
        self.camera_index = (self.camera_index + 1) % 4
        print(f"\nCycling to next camera index...")
        success = self._init_camera(self.camera_index)
        
        # If it failed, try to go back to 0 just in case
        if not success and self.camera_index != 0:
            print("Trying fallback to index 0...")
            self.camera_index = 0
            self._init_camera(0)

    # ── Fallback helpers ──────────────────────────────────────────────────
    def _make_fallback_duck(self):
        """Create a simple duck sprite when assets are missing."""
        surf = pygame.Surface((120, 100), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (139, 69, 19), [10, 30, 60, 30])
        pygame.draw.circle(surf, (34, 139, 34), (20, 35), 15)
        pygame.draw.circle(surf, (255, 255, 0), (18, 33), 3)
        return surf

    def _make_fallback_background(self):
        """Create a simple sky-and-grass background when assets are missing."""
        surf = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        surf.fill((135, 206, 235))
        pygame.draw.rect(surf, (34, 139, 34),
                         [0, 500, self.SCREEN_WIDTH, 220])
        return surf

    def _make_fallback_crosshair(self):
        """Create a simple crosshair sprite when assets are missing."""
        surf = pygame.Surface((80, 80), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 0, 0), (40, 40), 34, 3)
        pygame.draw.line(surf, (255, 0, 0), (40, 12), (40, 68), 2)
        pygame.draw.line(surf, (255, 0, 0), (12, 40), (68, 40), 2)
        pygame.draw.circle(surf, (255, 0, 0), (40, 40), 3)
        return surf

    def _save_current_score(self):
        """Save current game score to leaderboard (only once per game-over)."""
        if not self._game_over_scored:
            self._prev_high_score = get_high_score()
            add_score(
                self.game_engine.score,
                self.game_engine.get_accuracy(),
                self.game_engine.hits,
            )
            self._game_over_scored = True
    
    def process_camera_frame(self):
        # capture frame from webcam and detect hand
        if self.camera is None or not self.camera.isOpened():
            return None

        ret, frame = self.camera.read()
        
        if not ret:
            # Rate-limit camera failure logging (once per 5 seconds)
            now = time.time()
            if not hasattr(self, '_last_cam_fail_log') or now - self._last_cam_fail_log > 5:
                print("Warning: Camera read failed")
                self._last_cam_fail_log = now
            return None
        
        frame = cv2.flip(frame, 1)  # mirror the image
        
        # run hand detection
        gesture_data = self.gesture_detector.update(
            frame, 
            self.SCREEN_WIDTH, 
            self.SCREEN_HEIGHT
        )
        
        return gesture_data
    
    def draw_webcam_preview(self, frame):
        """Draw small webcam preview in corner"""
        if frame is None or not self.show_webcam:
            return
        
        # Resize frame
        preview_width = 320
        preview_height = 240
        frame_resized = cv2.resize(frame, (preview_width, preview_height))
        
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        
        # Convert to Pygame surface
        frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
        
        # Draw in bottom-right corner
        x = self.SCREEN_WIDTH - preview_width - 20
        y = self.SCREEN_HEIGHT - preview_height - 20
        
        # Draw border
        pygame.draw.rect(self.screen, (255, 255, 255), 
                        [x-2, y-2, preview_width+4, preview_height+4], 2)
        
        self.screen.blit(frame_surface, (x, y))
    
    def draw_gesture_indicator(self, is_finger_gun):
        # shows if hand gesture is detected or not
        if is_finger_gun:
            indicator_text = "FINGER GUN: READY ✓"
            color = (0, 255, 0)
        else:
            indicator_text = "FINGER GUN: NOT DETECTED"
            color = (255, 100, 100)
        
        text = self.font.render(indicator_text, True, color)
        self.screen.blit(text, (self.SCREEN_WIDTH - 450, 20))
    
    def draw_crosshair(self, position, recoil_offset=(0, 0)):
        """Draw crosshair at position with optional recoil"""
        if position is None:
            return
        
        x, y = position
        x += recoil_offset[0]
        y += recoil_offset[1]
        
        # Center the crosshair on the position
        crosshair_rect = self.crosshair.get_rect(center=(x, y))
        self.screen.blit(self.crosshair, crosshair_rect)
    
    def draw_game_over_screen(self):
        """Draw game over screen"""
        # Semi-transparent overlay
        self.screen.blit(self._full_overlay, (0, 0))
        
        # Game Over text
        title = self.title_font.render("GAME OVER", True, (255, 0, 0))
        title_rect = title.get_rect(center=(self.SCREEN_WIDTH // 2, 180))
        self.screen.blit(title, title_rect)

        # New high score celebration
        prev_high = getattr(self, '_prev_high_score', 0)
        if self.game_engine.score > prev_high and self.game_engine.score > 0:
            pulse = abs(int(time.time() * 3) % 2)
            celebration_color = (255, 215, 0) if pulse else (255, 100, 255)
            new_hs = self.title_font.render("NEW HIGH SCORE!", True, celebration_color)
            new_hs_rect = new_hs.get_rect(center=(self.SCREEN_WIDTH // 2, 250))
            self.screen.blit(new_hs, new_hs_rect)
        
        # Final stats
        score_text = self.font.render(f"Final Score: {self.game_engine.score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(self.SCREEN_WIDTH // 2, 300))
        self.screen.blit(score_text, score_rect)
        
        accuracy_text = self.font.render(
            f"Accuracy: {self.game_engine.get_accuracy():.1f}%", 
            True, (255, 255, 255)
        )
        accuracy_rect = accuracy_text.get_rect(center=(self.SCREEN_WIDTH // 2, 350))
        self.screen.blit(accuracy_text, accuracy_rect)
        
        hits_text = self.font.render(
            f"Ducks Shot: {self.game_engine.hits}", 
            True, (255, 255, 255)
        )
        hits_rect = hits_text.get_rect(center=(self.SCREEN_WIDTH // 2, 400))
        self.screen.blit(hits_text, hits_rect)

        escaped_text = self.font.render(
            f"Ducks Escaped: {self.game_engine.escaped_ducks}",
            True, (255, 150, 100)
        )
        escaped_rect = escaped_text.get_rect(center=(self.SCREEN_WIDTH // 2, 430))
        self.screen.blit(escaped_text, escaped_rect)

        if self.game_engine.best_streak >= 2:
            streak_text = self.font.render(
                f"Best Streak: {self.game_engine.best_streak}",
                True, (255, 100, 255)
            )
            streak_rect = streak_text.get_rect(center=(self.SCREEN_WIDTH // 2, 460))
            self.screen.blit(streak_text, streak_rect)

        if self.game_engine.highest_combo > 1.0:
            combo_text = self.font.render(
                f"Highest Combo: x{self.game_engine.highest_combo:.1f}",
                True, (255, 215, 0)
            )
            combo_rect = combo_text.get_rect(center=(self.SCREEN_WIDTH // 2, 490))
            self.screen.blit(combo_text, combo_rect)

        # High score
        high = get_high_score()
        if high > 0:
            hs_text = self.font.render(f"High Score: {high}", True, (255, 215, 0))
            hs_rect = hs_text.get_rect(center=(self.SCREEN_WIDTH // 2, 490))
            self.screen.blit(hs_text, hs_rect)
        
        # Instructions
        restart_text = self.font.render("R - Restart    M - Menu    ESC - Quit", True, (255, 215, 0))
        restart_rect = restart_text.get_rect(center=(self.SCREEN_WIDTH // 2, 550))
        self.screen.blit(restart_text, restart_rect)

    def draw_menu_screen(self):
        """Draw main menu screen"""
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill((135, 206, 235))

        self.screen.blit(self._menu_overlay, (0, 0))

        # Title
        title = self.title_font.render("DUCK HUNTER", True, (255, 215, 0))
        title_rect = title.get_rect(center=(self.SCREEN_WIDTH // 2, 140))
        self.screen.blit(title, title_rect)

        subtitle = self.font.render("Finger Gun Edition", True, (255, 255, 255))
        sub_rect = subtitle.get_rect(center=(self.SCREEN_WIDTH // 2, 200))
        self.screen.blit(subtitle, sub_rect)

        version = self.hint_font.render("v1.0.0", True, (150, 150, 150))
        ver_rect = version.get_rect(center=(self.SCREEN_WIDTH // 2, 235))
        self.screen.blit(version, ver_rect)

        # High score
        high = get_high_score()
        if high > 0:
            hs_text = self.font.render(f"High Score: {high}", True, (255, 215, 0))
            hs_rect = hs_text.get_rect(center=(self.SCREEN_WIDTH // 2, 250))
            self.screen.blit(hs_text, hs_rect)

        # Top 5 leaderboard
        scores = get_scores()
        if scores:
            lb_title = self.font.render("-- LEADERBOARD --", True, (255, 215, 0))
            lb_rect = lb_title.get_rect(center=(self.SCREEN_WIDTH // 2, 290))
            self.screen.blit(lb_title, lb_rect)
            for i, entry in enumerate(scores[:5]):
                date_str = ""
                if "timestamp" in entry:
                    import datetime
                    dt = datetime.datetime.fromtimestamp(entry["timestamp"])
                    date_str = f"  {dt.month}/{dt.day}"
                line = f"{i+1}. {entry['score']}  ({entry['accuracy']}%){date_str}"
                color = (255, 215, 0) if i == 0 else (200, 200, 200)
                text = self.font.render(line, True, color)
                rect = text.get_rect(center=(self.SCREEN_WIDTH // 2, 320 + i * 28))
                self.screen.blit(text, rect)

        # Controls
        controls = [
            "Make a finger gun pose to aim",
            "Quick thumb down-up motion to shoot",
            "",
            "P - Pause    W - Webcam    M - Mute",
            "F - FPS      H - Hitbox    C - Camera",
            "\u2191\u2193 - Volume    R - Restart  ESC - Quit",
        ]
        for i, line in enumerate(controls):
            color = (200, 200, 200)
            text = self.font.render(line, True, color)
            rect = text.get_rect(center=(self.SCREEN_WIDTH // 2, 490 + i * 28))
            self.screen.blit(text, rect)

        # Start prompt
        start_text = self.font.render("Press SPACE to Start", True, (255, 255, 0))
        start_rect = start_text.get_rect(center=(self.SCREEN_WIDTH // 2, 670))
        self.screen.blit(start_text, start_rect)

        # Quit confirmation
        if self._quit_confirm:
            confirm = self.title_font.render("Really quit? (Y / N)", True, (255, 80, 80))
            confirm_rect = confirm.get_rect(center=(self.SCREEN_WIDTH // 2, 620))
            bg = pygame.Surface((confirm.get_width() + 30, confirm.get_height() + 10), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 200))
            self.screen.blit(bg, (confirm_rect.x - 15, confirm_rect.y - 5))
            self.screen.blit(confirm, confirm_rect)
    
    def handle_events(self):
        """Handle Pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_engine.state == GameState.MENU:
                        self._quit_confirm = not self._quit_confirm
                    else:
                        self.running = False

                elif event.key == pygame.K_y and self._quit_confirm:
                    self.running = False

                elif event.key == pygame.K_n and self._quit_confirm:
                    self._quit_confirm = False

                elif event.key == pygame.K_SPACE:
                    if self.game_engine.state == GameState.MENU:
                        self.game_engine.state = GameState.PLAYING
                        self._music_faded_out = False
                        if not self.music_muted:
                            pygame.mixer.music.play(-1)

                elif event.key == pygame.K_r and self.game_engine.state == GameState.GAME_OVER:
                    self._save_current_score()
                    # Restart game
                    self.game_engine.reset()
                    self._game_over_scored = False
                    self._music_faded_out = False
                    # Resume music
                    if not self.music_muted:
                        pygame.mixer.music.play(-1)

                elif event.key == pygame.K_m:
                    if self.game_engine.state == GameState.GAME_OVER:
                        # Save score and go back to menu
                        self._save_current_score()
                        self.game_engine.reset()
                        self.game_engine.state = GameState.MENU
                        self._game_over_scored = False
                        self._music_faded_out = False
                    else:
                        # Toggle background music mute
                        self.music_muted = not self.music_muted
                        if self.music_muted:
                            pygame.mixer.music.pause()
                        else:
                            pygame.mixer.music.unpause()

                elif event.key == pygame.K_w:
                    # Toggle webcam preview
                    self.show_webcam = not self.show_webcam

                elif event.key == pygame.K_f:
                    # Toggle FPS display
                    self.show_fps = not self.show_fps

                elif event.key == pygame.K_h:
                    # Toggle hitbox debug view
                    self.show_hitbox = not self.show_hitbox

                elif event.key == pygame.K_p:
                    # Toggle pause
                    if self.game_engine.state in (GameState.PLAYING, GameState.PAUSED):
                        self.game_engine.toggle_pause()

                elif event.key == pygame.K_c:
                    # Cycle camera index
                    self.cycle_camera()

                elif event.key == pygame.K_UP:
                    self.music_volume = min(1.0, self.music_volume + 0.1)
                    pygame.mixer.music.set_volume(self.music_volume)
                    self._volume_timer = pygame.time.get_ticks()

                elif event.key == pygame.K_DOWN:
                    self.music_volume = max(0.0, self.music_volume - 0.1)
                    pygame.mixer.music.set_volume(self.music_volume)
                    self._volume_timer = pygame.time.get_ticks()
    
    def run(self):
        """Main game loop"""
        print("\n" + "="*50)
        print("FINGER GUN DUCK HUNTER")
        print("="*50)
        print("\nControls:")
        print("  - Form FINGER GUN pose (index out, thumb up, others curled)")
        print("  - Aim with index finger")
        print("  - Pull trigger with quick thumb down-up motion to SHOOT")
        print("\nKeys:")
        print("  - Press W to toggle webcam preview")
        print("  - Press C to cycle cameras (if not working)")
        print("  - Press F to toggle FPS display")
        print("  - Press P to pause/resume")
        print("  - Press M to mute/unmute background music")
        print("  - Press ESC to quit")
        print("\nStarting game...\n")
        
        while self.running:
            # Handle events
            self.handle_events()
            
            # Process camera frame and detect gestures (skip when not playing)
            gesture_data = None
            if self.game_engine.state == GameState.PLAYING:
                gesture_data = self.process_camera_frame()
            
            if gesture_data:
                aim_pos = gesture_data['aim_pos']
                is_finger_gun = gesture_data['is_finger_gun']
                trigger_pulled = gesture_data['trigger_pulled']
                debug_frame = gesture_data['debug_frame']
                
                # Only shoot when actively playing (not paused)
                if trigger_pulled and is_finger_gun and aim_pos and self.game_engine.state == GameState.PLAYING:
                    hit = self.game_engine.shoot(aim_pos[0], aim_pos[1])
                    # Play gunshot sound
                    if self.gunshot_sound:
                        self.gunshot_sound.play()
                    # Screen shake on shot
                    self.shake_intensity = 8 if hit else 4
                    if hit:
                        print(f"💥 HIT! Score: {self.game_engine.score}")
                    else:
                        print(f"❌ MISS! Ammo: {self.game_engine.ammo}")
            else:
                debug_frame = None
                aim_pos = None
                is_finger_gun = False
            
            # Update game logic (skips if paused internally)
            self.game_engine.update()

            # Update screen shake
            if self.shake_intensity > 0.5:
                self.shake_offset[0] = random.randint(-int(self.shake_intensity), int(self.shake_intensity))
                self.shake_offset[1] = random.randint(-int(self.shake_intensity), int(self.shake_intensity))
                self.shake_intensity *= self.shake_decay
            else:
                self.shake_offset = [0, 0]
                self.shake_intensity = 0

            # Draw entire scene with shake offset
            sx, sy = self.shake_offset
            self.game_engine.draw_scene(self.screen, show_hitbox=self.show_hitbox, offset=(sx, sy))
            
            # UI
            self.game_engine.draw_ui(self.screen, self.font)
            
            # Crosshair (with recoil)
            if aim_pos and is_finger_gun:
                recoil = self.game_engine.recoil_offset if self.game_engine.recoil_active else (0, 0)
                self.draw_crosshair(aim_pos, recoil)
            
            # Effects
            if aim_pos:
                self.game_engine.draw_effects(self.screen, aim_pos)
            
            # Gesture indicator
            self.draw_gesture_indicator(is_finger_gun)
            
            # Webcam preview
            self.draw_webcam_preview(debug_frame)
            
            # FPS counter
            if self.show_fps:
                fps_text = self.font.render(f"FPS: {int(self.clock.get_fps())}", True, (255, 255, 0))
                self.screen.blit(fps_text, (self.SCREEN_WIDTH - 150, 60))

            # Keybind hints (during gameplay only)
            if self.game_engine.state == GameState.PLAYING:
                hints = self.hint_font.render(
                    "P: Pause  W: Webcam  F: FPS  H: Hitbox  M: Mute  C: Camera  \u2191\u2193: Volume",
                    True, (180, 180, 180)
                )
                hints_rect = hints.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT - 15))
                self.screen.blit(hints, hints_rect)
            
            # Game over screen
            if self.game_engine.state == GameState.GAME_OVER:
                self._save_current_score()
                self.draw_game_over_screen()
                # Fade out music on game over (only once)
                if not self._music_faded_out and pygame.mixer.music.get_busy() and not self.music_muted:
                    pygame.mixer.music.fadeout(2000)
                    self._music_faded_out = True
            
            # Pause overlay
            if self.game_engine.state == GameState.PAUSED:
                self.game_engine.draw_pause_overlay(self.screen)

            # Menu overlay
            if self.game_engine.state == GameState.MENU:
                self.draw_menu_screen()
            
            # Camera not available warning
            if self.camera is None and self.game_engine.state == GameState.PLAYING:
                warn = self.warn_font.render("No camera detected - use mouse fallback", True, (255, 200, 50))
                warn_rect = warn.get_rect(center=(self.SCREEN_WIDTH // 2, 50))
                self.screen.blit(warn, warn_rect)

            # Volume indicator
            if self._volume_timer > 0 and pygame.time.get_ticks() - self._volume_timer < 1200:
                bars = int(self.music_volume * 10)
                vol_text = self.vol_font.render(f"Volume: [{'#' * bars}{'.' * (10 - bars)}] {int(self.music_volume * 100)}%", True, (200, 200, 200))
                vol_rect = vol_text.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT - 40))
                bg = pygame.Surface((vol_text.get_width() + 20, vol_text.get_height() + 8), pygame.SRCALPHA)
                bg.fill((0, 0, 0, 150))
                self.screen.blit(bg, (vol_rect.x - 10, vol_rect.y - 4))
                self.screen.blit(vol_text, vol_rect)
            elif self._volume_timer > 0 and pygame.time.get_ticks() - self._volume_timer >= 1200:
                self._volume_timer = 0
            
            # Update display
            pygame.display.flip()
            
            # Control frame rate
            self.clock.tick(self.FPS)
        
        # Cleanup
        self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        print("\nCleaning up...")
        if self.camera:
            self.camera.release()
        self.gesture_detector.close()
        pygame.quit()
        print("Game closed. Thanks for playing!")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Finger Gun Duck Hunter - gesture-controlled duck hunting game")
    parser.add_argument("--version", action="version", version="Duck Hunter v1.0")
    parser.add_argument("--no-camera", action="store_true", help="Skip camera initialization (for testing)")
    args = parser.parse_args()

    game = FingerGunDuckHunter()
    if args.no_camera:
        game.camera = None
    game.run()
