import pygame
import sys
import math
import random
import os

# Initialize Pygame and its mixer.
pygame.init()
pygame.mixer.init()

# --------------- Global Variables and Constants ---------------
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors.
WHITE      = (255, 255, 255)
BLACK      = (0, 0, 0)
DARKGRAY   = (40, 40, 40)
LIGHTGRAY  = (200, 200, 200)
ACCENT     = (30, 144, 255)

# Game states.
STATE_MENU   = "menu"
STATE_GAME   = "game"
STATE_PAUSE  = "pause"
STATE_WIN    = "win"
STATE_LOSE   = "lose"

# Global variables for background music.
current_bg_track = None
MUSIC_PAUSED = False

# --------------- Asset Filenames ---------------
# Change these filenames/paths as desired.
BACKGROUND_FILENAME = "background.gif"
TITLE_FILENAME      = "main_menu_logo.png"       # Title screen asset.
PADDLE_FILENAME     = "paddle.png"
BALL_FILENAME       = "ball.png"
BUTTON_FILENAME     = "button.png"

# --------------- Audio Helper Functions ---------------
def play_sound(name, volume=0.7):
    """
    Plays a sound effect via a mixer Sound object.
    The volume is normalized (default is 70%).
    """
    try:
        sound = pygame.mixer.Sound(name)
        sound.set_volume(volume)
        sound.play()
    except Exception as e:
        print(f"[SOUND] Error playing sound {name}: {e}")

def play_background_music(track_name, volume=0.3):
    """
    Loads and plays background music on a loop.
    The volume is normalized (default is 30%).
    If the requested track is already loaded and paused, simply unpause it.
    """
    global current_bg_track, MUSIC_PAUSED
    if current_bg_track == track_name:
        if MUSIC_PAUSED:
            pygame.mixer.music.unpause()
            MUSIC_PAUSED = False
        return
    else:
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        current_bg_track = track_name
        MUSIC_PAUSED = False
        try:
            pygame.mixer.music.load(track_name)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"[MUSIC] Error loading music {track_name}: {e}")

def stop_background_music():
    """
    Stops any background music.
    """
    global current_bg_track, MUSIC_PAUSED
    current_bg_track = None
    MUSIC_PAUSED = False
    pygame.mixer.music.stop()

# --------------- Customizable Drawable Classes ---------------
class Button:
    def __init__(self, text, pos, font, base_color=LIGHTGRAY, hover_color=ACCENT, font_name="Arial", image=None):
        self.text = text
        self.pos = pos  # Center position.
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color
        self.current_color = base_color
        self.font_name = font_name
        self.image = image  # Optional image for the button.
        self.render_text = self.font.render(self.text, True, self.current_color)
        self.rect = self.render_text.get_rect(center=self.pos)
        self.scale = 1.0
        self.target_scale = 1.0

    def update(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.current_color = self.hover_color
            self.target_scale = 1.1
        else:
            self.current_color = self.base_color
            self.target_scale = 1.0

        self.scale += (self.target_scale - self.scale) * 0.2
        font_size = max(1, int(self.font.get_height() * self.scale))
        font = pygame.font.SysFont(self.font_name, font_size)
        self.render_text = font.render(self.text, True, self.current_color)
        self.rect = self.render_text.get_rect(center=self.pos)

    def draw(self, screen):
        if self.image:
            img = pygame.transform.scale(self.image, (self.rect.width + 20, self.rect.height + 10))
            img_rect = img.get_rect(center=self.pos)
            screen.blit(img, img_rect)
        else:
            pygame.draw.rect(screen, DARKGRAY, self.rect.inflate(20, 10))
        screen.blit(self.render_text, self.rect)

    def is_clicked(self, mouse_pos, mouse_pressed):
        return self.rect.collidepoint(mouse_pos) and mouse_pressed

class Paddle:
    def __init__(self, x, y, width=10, height=100, speed=7, image=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.image = image  # Optional image for the paddle.

    def move(self, dy):
        self.rect.y += dy
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def draw(self, screen):
        if self.image:
            img = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))
            screen.blit(img, self.rect)
        else:
            pygame.draw.rect(screen, WHITE, self.rect)

class Ball:
    def __init__(self, x, y, radius=10, speed=5, image=None):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed
        self.image = image  # Optional image for the ball.
        self.angle = math.radians(45)
        self.dx = math.cos(self.angle) * self.speed
        self.dy = math.sin(self.angle) * self.speed
        self.hit_flash = 0

    def update(self):
        self.x += self.dx
        self.y += self.dy

        # Bounce off top/bottom.
        if self.y - self.radius < 0 or self.y + self.radius > HEIGHT:
            self.dy *= -1
            play_sound("ball_hit.mp3")
        if self.hit_flash > 0:
            self.hit_flash -= 1

    def draw(self, screen):
        if self.image:
            diameter = self.radius * 2
            img = pygame.transform.scale(self.image, (diameter, diameter))
            img_rect = img.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(img, img_rect)
        else:
            color = WHITE if self.hit_flash == 0 else ACCENT
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)

    def reset(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.angle = math.radians(45)
        self.dx = math.cos(self.angle) * self.speed * (1 if pygame.time.get_ticks() % 2 == 0 else -1)
        self.dy = math.sin(self.angle) * self.speed

# --------------- Pong Game Class ---------------
class PongGame:
    def __init__(self, sound_on=True, paddle_img=None, ball_img=None):
        self.player = Paddle(30, HEIGHT // 2 - 50, image=paddle_img)
        self.cpu = Paddle(WIDTH - 40, HEIGHT // 2 - 50, image=paddle_img)
        self.ball = Ball(WIDTH // 2, HEIGHT // 2, image=ball_img)
        self.sound_on = sound_on

        self.player_score = 0
        self.cpu_score = 0
        self.winning_score = 10
        self.explosion_event = None

    def update(self, keys):
        # Player controls.
        if keys[pygame.K_w]:
            self.player.move(-self.player.speed)
        if keys[pygame.K_s]:
            self.player.move(self.player.speed)

        # ----- CPU AI with Dynamic Error -----
        if self.ball.dx > 0:
            time_to_reach = (self.cpu.rect.left - self.ball.x) / self.ball.dx if self.ball.dx != 0 else 0
            predicted_y = self.ball.y + self.ball.dy * time_to_reach
            while predicted_y < 0 or predicted_y > HEIGHT:
                if predicted_y < 0:
                    predicted_y = -predicted_y
                elif predicted_y > HEIGHT:
                    predicted_y = 2 * HEIGHT - predicted_y
            # Dynamic error amplitude: large when player score is 0, small near winning score.
            max_error = 50
            min_error = 5
            # Clamp player's score between 0 and winning_score.
            score_factor = min(max(self.player_score, 0), self.winning_score)
            error_amplitude = max_error - ((score_factor / self.winning_score) * (max_error - min_error))
            error = random.uniform(-error_amplitude, error_amplitude)
            target_y = predicted_y + error
        else:
            target_y = HEIGHT / 2

        if self.cpu.rect.centery < target_y:
            self.cpu.move(self.cpu.speed * 0.7)
        elif self.cpu.rect.centery > target_y:
            self.cpu.move(-self.cpu.speed * 0.7)
        # --------------------------------------

        self.ball.update()

        # ----- Collision Detection -----
        if self.player.rect.collidepoint(self.ball.x - self.ball.radius, self.ball.y):
            if self.ball.dx < 0:
                self.ball.dx *= -1
                self.ball.hit_flash = 10
                if self.sound_on:
                    play_sound("ball_hit.mp3")
        if self.cpu.rect.collidepoint(self.ball.x + self.ball.radius, self.ball.y):
            if self.ball.dx > 0:
                self.ball.dx *= -1
                self.ball.hit_flash = 10
                if self.sound_on:
                    play_sound("ball_hit.mp3")
        # --------------------------------

        # ----- Scoring -----
        if self.ball.x < 0:
            self.cpu_score += 1
            if self.sound_on:
                play_sound("score.mp3")
            self.ball.speed += 0.5
            self.explosion_event = "lose"
            self.ball.reset()
        if self.ball.x > WIDTH:
            self.player_score += 1
            if self.sound_on:
                play_sound("score.mp3")
            self.ball.speed += 0.5
            self.explosion_event = "win"
            self.ball.reset()
        # -------------------
        
    def draw(self, screen):
        pygame.draw.aaline(screen, LIGHTGRAY, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))
        self.player.draw(screen)
        self.cpu.draw(screen)
        self.ball.draw(screen)
        font = pygame.font.SysFont("Arial", 36)
        score_text = font.render(f"{self.player_score}   {self.cpu_score}", True, WHITE)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))

    def game_over(self):
        if self.player_score >= self.winning_score:
            return STATE_WIN
        if self.cpu_score >= self.winning_score:
            return STATE_LOSE
        return None

# --------------- Main Application Class ---------------
class App:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("PyPong 2025")
        self.clock = pygame.time.Clock()
        self.state = STATE_MENU
        self.sound_on = True

        self.menu_font = pygame.font.SysFont("Arial", 30)
        self.title_font = pygame.font.SysFont("Arial", 80)

        # Load assets.
        self.background_image = self.load_image(BACKGROUND_FILENAME, (WIDTH, HEIGHT))
        self.title_image = self.load_image(TITLE_FILENAME)  # Title asset.
        self.paddle_image = self.load_image(PADDLE_FILENAME)
        self.ball_image = self.load_image(BALL_FILENAME)
        self.button_image = self.load_image(BUTTON_FILENAME)

        self.buttons = {
            "start": Button("Start Game - VS CPU", (WIDTH // 2, HEIGHT // 2 - 20), self.menu_font, font_name="Arial", image=self.button_image),
            "sound": Button("Sound - ON", (WIDTH // 2, HEIGHT // 2 + 40), self.menu_font, font_name="Arial", image=self.button_image),
            "quit":  Button("Quit", (WIDTH // 2, HEIGHT // 2 + 100), self.menu_font, font_name="Arial", image=self.button_image)
        }
        self.game = None

    def load_image(self, filename, size=None):
        if not os.path.exists(filename):
            return None
        try:
            img = pygame.image.load(filename).convert_alpha()
            if size:
                img = pygame.transform.scale(img, size)
            return img
        except Exception as e:
            print(f"[ASSETS] Error loading {filename}: {e}")
            return None

    def show_explosion_popup(self, message, sound_file):
        if self.sound_on:
            play_sound(sound_file)
        popup_duration = 1500  # milliseconds.
        start_time = pygame.time.get_ticks()
        big_font = pygame.font.SysFont("Arial", 100)
        while pygame.time.get_ticks() - start_time < popup_duration:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            if self.background_image:
                self.screen.blit(self.background_image, (0, 0))
            else:
                self.screen.fill(DARKGRAY)
            text_surf = big_font.render(message, True, ACCENT)
            text_rect = text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.screen.blit(text_surf, text_rect)
            pygame.display.flip()

    def run(self):
        while True:
            if self.state == STATE_MENU:
                self.menu_loop()
            elif self.state == STATE_GAME:
                self.game_loop()
            elif self.state == STATE_PAUSE:
                self.pause_loop()
            elif self.state in (STATE_WIN, STATE_LOSE):
                self.end_loop()
            else:
                pygame.quit()
                sys.exit()

    def menu_loop(self):
        if self.sound_on:
            play_background_music("bg.mp3")
        else:
            stop_background_music()
        while self.state == STATE_MENU:
            self.clock.tick(FPS)
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pressed = True
            for button in self.buttons.values():
                button.update(mouse_pos)
            if self.buttons["start"].is_clicked(mouse_pos, mouse_pressed):
                self.game = PongGame(sound_on=self.sound_on, paddle_img=self.paddle_image, ball_img=self.ball_image)
                self.state = STATE_GAME
            elif self.buttons["sound"].is_clicked(mouse_pos, mouse_pressed):
                self.sound_on = not self.sound_on
                sound_text = "Sound - ON" if self.sound_on else "Sound - OFF"
                self.buttons["sound"].text = sound_text
                if self.sound_on:
                    play_background_music("bg.mp3")
                else:
                    stop_background_music()
            elif self.buttons["quit"].is_clicked(mouse_pos, mouse_pressed):
                pygame.quit()
                sys.exit()
            # Draw background.
            if self.background_image:
                self.screen.blit(self.background_image, (0, 0))
            else:
                self.screen.fill(DARKGRAY)
            # ----- Title Screen (Animated) -----
            # If a title image is loaded, animate it with a pulsating (scaling) effect.
            if self.title_image:
                # Compute scale factor based on time (sine wave).
                scale_factor = 1 + 0.05 * math.sin(pygame.time.get_ticks() * 0.002)
                img_width = int(self.title_image.get_width() * scale_factor)
                img_height = int(self.title_image.get_height() * scale_factor)
                title_img = pygame.transform.scale(self.title_image, (img_width, img_height))
                title_rect = title_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 150))
                self.screen.blit(title_img, title_rect)
            else:
                # Fallback animated text title.
                scale_factor = 1 + 0.05 * math.sin(pygame.time.get_ticks() * 0.002)
                font_size = int(80 * scale_factor)
                anim_font = pygame.font.SysFont("Arial", font_size)
                title_surf = anim_font.render("Ping Pong", True, WHITE)
                title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 150))
                self.screen.blit(title_surf, title_rect)
            # Draw buttons.
            for button in self.buttons.values():
                button.draw(self.screen)
            pygame.display.flip()

    def game_loop(self):
        if self.sound_on:
            play_background_music("game_music.mp3")
        else:
            stop_background_music()
        while self.state == STATE_GAME:
            self.clock.tick(FPS)
            keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if self.sound_on and not MUSIC_PAUSED:
                        pygame.mixer.music.pause()
                        globals()['MUSIC_PAUSED'] = True
                    self.state = STATE_PAUSE
                    break
            if self.state == STATE_GAME:
                self.game.update(keys)
                if self.game.explosion_event is not None:
                    if self.game.explosion_event == "win":
                        self.show_explosion_popup("You Win!", "boom_win.mp3")
                    elif self.game.explosion_event == "lose":
                        self.show_explosion_popup("You Lose!", "boom_lose.mp3")
                    self.game.explosion_event = None
                new_state = self.game.game_over()
                if new_state is not None:
                    self.state = new_state
                if self.background_image:
                    self.screen.blit(self.background_image, (0, 0))
                else:
                    self.screen.fill(BLACK)
                self.game.draw(self.screen)
                pygame.display.flip()

    def pause_loop(self):
        pause_font = pygame.font.SysFont("Arial", 40)
        resume_button = Button("Resume", (WIDTH // 2, HEIGHT // 2 - 40), pause_font, font_name="Arial", image=self.button_image)
        menu_button = Button("Main Menu", (WIDTH // 2, HEIGHT // 2 + 20), pause_font, font_name="Arial", image=self.button_image)
        quit_button = Button("Quit", (WIDTH // 2, HEIGHT // 2 + 80), pause_font, font_name="Arial", image=self.button_image)
        buttons = [resume_button, menu_button, quit_button]
        while self.state == STATE_PAUSE:
            self.clock.tick(FPS)
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pressed = True
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.state = STATE_GAME
                    if self.sound_on and MUSIC_PAUSED:
                        pygame.mixer.music.unpause()
                        globals()['MUSIC_PAUSED'] = False
                    break
            for button in buttons:
                button.update(mouse_pos)
            if resume_button.is_clicked(mouse_pos, mouse_pressed):
                self.state = STATE_GAME
                if self.sound_on and MUSIC_PAUSED:
                    pygame.mixer.music.unpause()
                    globals()['MUSIC_PAUSED'] = False
            elif menu_button.is_clicked(mouse_pos, mouse_pressed):
                self.state = STATE_MENU
                if self.sound_on:
                    play_background_music("bg.mp3")
            elif quit_button.is_clicked(mouse_pos, mouse_pressed):
                pygame.quit()
                sys.exit()
            if self.background_image:
                self.screen.blit(self.background_image, (0, 0))
            else:
                self.screen.fill(DARKGRAY)
            pause_title = pygame.font.SysFont("Arial", 60).render("Paused", True, ACCENT)
            title_rect = pause_title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 120))
            self.screen.blit(pause_title, title_rect)
            for button in buttons:
                button.draw(self.screen)
            pygame.display.flip()

    def end_loop(self):
        font = pygame.font.SysFont("Arial", 60)
        message = "You Win!" if self.state == STATE_WIN else "You Lose!"
        counter = 0
        while self.state in (STATE_WIN, STATE_LOSE):
            self.clock.tick(FPS)
            counter += 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    self.state = STATE_MENU
                    self.buttons["start"].text = "Start Game - VS CPU"
                    self.buttons["sound"].text = "Sound - ON" if self.sound_on else "Sound - OFF"
                    if self.sound_on:
                        play_background_music("bg.mp3")
                    break
            scale = 1 + 0.1 * math.sin(counter * 0.1)
            font_size = int(60 * scale)
            anim_font = pygame.font.SysFont("Arial", font_size)
            text_surf = anim_font.render(message, True, ACCENT)
            text_rect = text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            if self.background_image:
                self.screen.blit(self.background_image, (0, 0))
            else:
                self.screen.fill(DARKGRAY)
            self.screen.blit(text_surf, text_rect)
            pygame.display.flip()

if __name__ == "__main__":
    app = App()
    app.run()
