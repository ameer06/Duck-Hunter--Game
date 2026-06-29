# Duck Hunter Game - Gesture Controlled!
# Made by: Mohamed
# Uses hand tracking to shoot ducks (like the classic Duck Hunt)

import pygame
import cv2
import sys
import numpy as np
from hand_gesture import HandGestureDetector
from game_engine import GameEngine, GameState
from highscore import add_score, get_high_score, get_scores


class FingerGunDuckHunter:
    # main game class - handles everything
    
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
        except Exception:
            pass
        
        self.running = True
        self.show_webcam = True  # press W to toggle
        self.show_fps = True
        self._game_over_scored = False
        
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
            pygame.mixer.music.set_volume(0.45)
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
        self.camera = cv2.VideoCapture(index)
        
        if self.camera.isOpened():
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            print(f"✓ Camera {index} opened successfully")
            return True
        else:
            print(f"⚠ Failed to open camera index {index}")
            return False

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
        surf = pygame.Surface((120, 100), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (139, 69, 19), [10, 30, 60, 30])
        pygame.draw.circle(surf, (34, 139, 34), (20, 35), 15)
        pygame.draw.circle(surf, (255, 255, 0), (18, 33), 3)
        return surf

    def _make_fallback_background(self):
        surf = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        surf.fill((135, 206, 235))
        pygame.draw.rect(surf, (34, 139, 34),
                         [0, 500, self.SCREEN_WIDTH, 220])
        return surf

    def _make_fallback_crosshair(self):
        surf = pygame.Surface((80, 80), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 0, 0), (40, 40), 34, 3)
        pygame.draw.line(surf, (255, 0, 0), (40, 12), (40, 68), 2)
        pygame.draw.line(surf, (255, 0, 0), (12, 40), (68, 40), 2)
        pygame.draw.circle(surf, (255, 0, 0), (40, 40), 3)
        return surf
    
    def process_camera_frame(self):
        # capture frame from webcam and detect hand
        ret, frame = self.camera.read()
        
        if not ret:
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
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Game Over text
        title = self.title_font.render("GAME OVER", True, (255, 0, 0))
        title_rect = title.get_rect(center=(self.SCREEN_WIDTH // 2, 200))
        self.screen.blit(title, title_rect)
        
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

        # High score
        high = get_high_score()
        if high > 0:
            hs_text = self.font.render(f"High Score: {high}", True, (255, 215, 0))
            hs_rect = hs_text.get_rect(center=(self.SCREEN_WIDTH // 2, 450))
            self.screen.blit(hs_text, hs_rect)
        
        # Instructions
        restart_text = self.font.render("Press R to Restart or ESC to Quit", True, (255, 215, 0))
        restart_rect = restart_text.get_rect(center=(self.SCREEN_WIDTH // 2, 530))
        self.screen.blit(restart_text, restart_rect)

    def draw_menu_screen(self):
        """Draw main menu screen"""
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill((135, 206, 235))

        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        overlay.set_alpha(160)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Title
        title = self.title_font.render("DUCK HUNTER", True, (255, 215, 0))
        title_rect = title.get_rect(center=(self.SCREEN_WIDTH // 2, 140))
        self.screen.blit(title, title_rect)

        subtitle = self.font.render("Finger Gun Edition", True, (255, 255, 255))
        sub_rect = subtitle.get_rect(center=(self.SCREEN_WIDTH // 2, 200))
        self.screen.blit(subtitle, sub_rect)

        # High score
        high = get_high_score()
        if high > 0:
            hs_text = self.font.render(f"High Score: {high}", True, (255, 215, 0))
            hs_rect = hs_text.get_rect(center=(self.SCREEN_WIDTH // 2, 250))
            self.screen.blit(hs_text, hs_rect)

        # Controls
        controls = [
            "Make a finger gun pose to aim",
            "Quick thumb down-up motion to shoot",
            "",
            "P - Pause    W - Webcam    M - Mute",
            "F - FPS      C - Camera    ESC - Quit",
        ]
        for i, line in enumerate(controls):
            color = (200, 200, 200) if line else (200, 200, 200)
            text = self.font.render(line, True, color)
            rect = text.get_rect(center=(self.SCREEN_WIDTH // 2, 320 + i * 35))
            self.screen.blit(text, rect)

        # Start prompt
        start_text = self.font.render("Press SPACE to Start", True, (255, 255, 0))
        start_rect = start_text.get_rect(center=(self.SCREEN_WIDTH // 2, 560))
        self.screen.blit(start_text, start_rect)
    
    def handle_events(self):
        """Handle Pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                elif event.key == pygame.K_SPACE:
                    if self.game_engine.state == GameState.MENU:
                        self.game_engine.state = GameState.PLAYING
                        if not self.music_muted:
                            pygame.mixer.music.play(-1)

                elif event.key == pygame.K_r and self.game_engine.state == GameState.GAME_OVER:
                    # Save score before restart
                    add_score(
                        self.game_engine.score,
                        self.game_engine.get_accuracy(),
                        self.game_engine.hits,
                    )
                    # Restart game
                    self.game_engine.reset()
                    self._game_over_scored = False
                    # Resume music
                    if not self.music_muted:
                        pygame.mixer.music.play(-1)
                
                elif event.key == pygame.K_w:
                    # Toggle webcam preview
                    self.show_webcam = not self.show_webcam
                
                elif event.key == pygame.K_f:
                    # Toggle FPS display
                    self.show_fps = not self.show_fps

                elif event.key == pygame.K_m:
                    # Toggle background music mute
                    self.music_muted = not self.music_muted
                    if self.music_muted:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()

                elif event.key == pygame.K_p:
                    # Toggle pause
                    if self.game_engine.state in (GameState.PLAYING, GameState.PAUSED):
                        self.game_engine.toggle_pause()

                elif event.key == pygame.K_c:
                    # Cycle camera index
                    self.cycle_camera()
    
    def run(self):
        """Main game loop"""
        print("\n" + "="*50)
        print("🎮 FINGER GUN DUCK HUNTER 🦆")
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
            
            # Process camera frame and detect gestures
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
            
            # Draw entire scene (background → far trees → ducks → near trees → grass)
            self.game_engine.draw_scene(self.screen, show_hitbox=False)
            
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
            
            # Game over screen
            if self.game_engine.state == GameState.GAME_OVER:
                if not self._game_over_scored:
                    add_score(
                        self.game_engine.score,
                        self.game_engine.get_accuracy(),
                        self.game_engine.hits,
                    )
                    self._game_over_scored = True
                self.draw_game_over_screen()
                # Fade out music on game over (only once)
                if pygame.mixer.music.get_busy() and not self.music_muted:
                    pygame.mixer.music.fadeout(2000)
            
            # Pause overlay
            if self.game_engine.state == GameState.PAUSED:
                self.game_engine.draw_pause_overlay(self.screen)

            # Menu overlay
            if self.game_engine.state == GameState.MENU:
                self.draw_menu_screen()
            
            # Update display
            pygame.display.flip()
            
            # Control frame rate
            self.clock.tick(self.FPS)
        
        # Cleanup
        self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        print("\nCleaning up...")
        self.camera.release()
        self.gesture_detector.close()
        pygame.quit()
        print("Game closed. Thanks for playing! 🎮")


if __name__ == "__main__":
    game = FingerGunDuckHunter()
    game.run()
