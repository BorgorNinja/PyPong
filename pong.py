import pygame
import sys
import math

pygame.init()
pygame.mixer.init()

#All the Variables

WIDTH, HEIGHT = 800, 600
FPS = 60


WHITE      = (255, 255, 255)
BLACK      = (0, 0, 0)
DARKGRAY   = (40, 40, 40)
LIGHTGRAY  = (200, 200, 200)
ACCENT     = (30, 144, 255)


STATE_MENU   = "menu"
STATE_GAME   = "game"
STATE_PAUSE  = "pause"
STATE_WIN    = "win"
STATE_LOSE   = "lose"


current_bg_track = None

# Placeholder for playing a sound effect
def play_sound(name):
    # Function for loading sounds
    print(f"[SOUND] Playing sound: {name}")

# Placeholder for playing background music
def play_background_music(track_name):
    global current_bg_track
    if current_bg_track != track_name:
        current_bg_track = track_name
        # Load background music here (track_name can be anything like mp3 files)
        print(f"[MUSIC] Now playing background music: {track_name}")

# Optionally, a function to stop background music if needed.
def stop_background_music():
    global current_bg_track
    current_bg_track = None
    # In production, stop the music:
    # pygame.mixer.music.stop()
    print("[MUSIC] Background music stopped.")

# Class for buttons
class Button:
    def __init__(self, text, pos, font, base_color=LIGHTGRAY, hover_color=ACCENT, font_name="Arial"):
        self.text = text
        self.pos = pos  # Center position (x, y)
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color
        self.current_color = base_color
        self.font_name = font_name  # Store the font name for scaling
        self.render_text = self.font.render(self.text, True, self.current_color)
        self.rect = self.render_text.get_rect(center=self.pos)
        # Animation scale parameters
        self.scale = 1.0
        self.target_scale = 1.0

    def update(self, mouse_pos):
        # Check if the mouse is hovering over the button
        if self.rect.collidepoint(mouse_pos):
            self.current_color = self.hover_color
            self.target_scale = 1.1  # Make the button big and phat like your mom when hovered
        else:
            self.current_color = self.base_color
            self.target_scale = 1.0

        # AnImAtIons
        self.scale += (self.target_scale - self.scale) * 0.2
        # Re-render text with current color and scale
        font_size = max(1, int(self.font.get_height() * self.scale))
        font = pygame.font.SysFont(self.font_name, font_size)
        self.render_text = font.render(self.text, True, self.current_color)
        self.rect = self.render_text.get_rect(center=self.pos)

    def draw(self, screen):
        screen.blit(self.render_text, self.rect)

    def is_clicked(self, mouse_pos, mouse_pressed):
        return self.rect.collidepoint(mouse_pos) and mouse_pressed

# Paddle Class
class Paddle:
    def __init__(self, x, y, width=10, height=100, speed=7):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed

    def move(self, dy):
        self.rect.y += dy
        # Some scuffed code for preventing the paddle from going off screen
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def update(self):
        # put placeholder animation here
        pass

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect)

#Ball Class for the whole game basically
class Ball:
    def __init__(self, x, y, radius=10, speed=5):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed

        self.angle = math.radians(45)
        self.dx = math.cos(self.angle) * self.speed
        self.dy = math.sin(self.angle) * self.speed
        # ball change color when hitting the paddle
        self.hit_flash = 0

    def update(self):
        self.x += self.dx
        self.y += self.dy

        # Bounce off the top and bottom walls
        if self.y - self.radius < 0 or self.y + self.radius > HEIGHT:
            self.dy *= -1
            play_sound("wall_hit")

        # Decrease flash effect over time
        if self.hit_flash > 0:
            self.hit_flash -= 1

    def draw(self, screen):
        color = WHITE
        if self.hit_flash > 0:
            # Flash effect color
            color = ACCENT
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)

    def reset(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.angle = math.radians(45)
        #Random bounce direction when hitting wall
        self.dx = math.cos(self.angle) * self.speed * (1 if pygame.time.get_ticks() % 2 == 0 else -1)
        self.dy = math.sin(self.angle) * self.speed

# ---------------- Pong Game Class ----------------
class PongGame:
    def __init__(self, sound_on=True):
        # Create the player (left paddle) and CPU (right paddle)
        self.player = Paddle(30, HEIGHT // 2 - 50)
        self.cpu = Paddle(WIDTH - 40, HEIGHT // 2 - 50)
        self.ball = Ball(WIDTH // 2, HEIGHT // 2)
        self.sound_on = sound_on

        self.player_score = 0
        self.cpu_score = 0
        self.winning_score = 3

    def update(self, keys):
        # Player paddle movement (W and S keys)
        if keys[pygame.K_w]:
            self.player.move(-self.player.speed)
        if keys[pygame.K_s]:
            self.player.move(self.player.speed)

        # CPU AI here
        if self.ball.y < self.cpu.rect.centery:
            self.cpu.move(-self.cpu.speed * 0.7)
        elif self.ball.y > self.cpu.rect.centery:
            self.cpu.move(self.cpu.speed * 0.7)

        # Ball position update tick
        self.ball.update()

        # Clipping check for player paddle
        if self.player.rect.collidepoint(self.ball.x - self.ball.radius, self.ball.y):
            if self.ball.dx < 0:
                self.ball.dx *= -1
                self.ball.hit_flash = 10
                if self.sound_on:
                    play_sound("paddle_hit")
        # Same but for CPU paddle
        if self.cpu.rect.collidepoint(self.ball.x + self.ball.radius, self.ball.y):
            if self.ball.dx > 0:
                self.ball.dx *= -1
                self.ball.hit_flash = 10
                if self.sound_on:
                    play_sound("paddle_hit")

        # Win/Lose Stuff for ball going past the paddle
        if self.ball.x < 0:
            self.cpu_score += 1
            if self.sound_on:
                play_sound("score")
            self.ball.reset()
        if self.ball.x > WIDTH:
            self.player_score += 1
            if self.sound_on:
                play_sound("score")
            self.ball.reset()

    def draw(self, screen):
        # Draw the center dividing line
        pygame.draw.aaline(screen, LIGHTGRAY, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))
        # Draw paddles and the ball
        self.player.draw(screen)
        self.cpu.draw(screen)
        self.ball.draw(screen)

        # Draw scores at the top of the screen
        font = pygame.font.SysFont("Arial", 36)
        score_text = font.render(f"{self.player_score}   {self.cpu_score}", True, WHITE)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))

    def game_over(self):
        # Check if either side has reached the winning score
        if self.player_score >= self.winning_score:
            return STATE_WIN
        if self.cpu_score >= self.winning_score:
            return STATE_LOSE
        return None


#The main game class
class App:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("PyPong 2025")
        self.clock = pygame.time.Clock()

        # Initial state and sound setting
        self.state = STATE_MENU
        self.sound_on = True
        self.current_music = None

        # Setup fonts for menus
        self.menu_font = pygame.font.SysFont("Arial", 40)
        self.title_font = pygame.font.SysFont("Arial", 80)

        # Main menu buttons
        self.buttons = {
            "start": Button("Start Game - VS CPU", (WIDTH // 2, HEIGHT // 2 - 20), self.menu_font, font_name="Arial"),
            "sound": Button("Sound - ON", (WIDTH // 2, HEIGHT // 2 + 40), self.menu_font, font_name="Arial"),
            "quit":  Button("Quit", (WIDTH // 2, HEIGHT // 2 + 100), self.menu_font, font_name="Arial")
        }

        # Start game instance
        self.game = None

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
        # background music for main menu
        if self.sound_on:
            play_background_music("menu")

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

            # Update menu buttons
            for button in self.buttons.values():
                button.update(mouse_pos)

            # Check for button clicks
            if self.buttons["start"].is_clicked(mouse_pos, mouse_pressed):
                self.game = PongGame(sound_on=self.sound_on)
                self.state = STATE_GAME
            elif self.buttons["sound"].is_clicked(mouse_pos, mouse_pressed):
                self.sound_on = not self.sound_on
                sound_text = "Sound - ON" if self.sound_on else "Sound - OFF"
                self.buttons["sound"].text = sound_text
            elif self.buttons["quit"].is_clicked(mouse_pos, mouse_pressed):
                pygame.quit()
                sys.exit()

            # Draw the main menu background and title
            self.screen.fill(DARKGRAY)
            title_surf = self.title_font.render("Ping Pong", True, WHITE)
            title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
            self.screen.blit(title_surf, title_rect)

            # Draw the buttons
            for button in self.buttons.values():
                button.draw(self.screen)

            pygame.display.flip()

    def game_loop(self):
        # Set background music for game play
        if self.sound_on:
            play_background_music("game")

        while self.state == STATE_GAME:
            self.clock.tick(FPS)
            keys = pygame.key.get_pressed()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # If ESC is pressed, switch to pause menu
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.state = STATE_PAUSE
                    break

            # Update game objects only if still in game state
            if self.state == STATE_GAME:
                self.game.update(keys)
                new_state = self.game.game_over()
                if new_state is not None:
                    self.state = new_state

                self.screen.fill(BLACK)
                self.game.draw(self.screen)
                pygame.display.flip()

    def pause_loop(self):
        # Music for pause menu
        if self.sound_on:
            play_background_music("pause")

        # Pause menu buttons
        pause_font = pygame.font.SysFont("Arial", 40)
        resume_button = Button("Resume", (WIDTH // 2, HEIGHT // 2 - 40), pause_font, font_name="Arial")
        menu_button = Button("Main Menu", (WIDTH // 2, HEIGHT // 2 + 20), pause_font, font_name="Arial")
        quit_button   = Button("Quit", (WIDTH // 2, HEIGHT // 2 + 80), pause_font, font_name="Arial")
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
                # go back to game when ESC pressed again on pause
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.state = STATE_GAME
                    break

            for button in buttons:
                button.update(mouse_pos)

            if resume_button.is_clicked(mouse_pos, mouse_pressed):
                self.state = STATE_GAME
            elif menu_button.is_clicked(mouse_pos, mouse_pressed):
                self.state = STATE_MENU
            elif quit_button.is_clicked(mouse_pos, mouse_pressed):
                pygame.quit()
                sys.exit()

            # Pause menu background
            self.screen.fill(DARKGRAY)
            pause_title = pygame.font.SysFont("Arial", 60).render("Paused", True, ACCENT)
            title_rect = pause_title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 120))
            self.screen.blit(pause_title, title_rect)

            for button in buttons:
                button.draw(self.screen)

            pygame.display.flip()

    def end_loop(self):
        # End screen for win/lose
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
                # Return to main menu on key press or mouse click
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    self.state = STATE_MENU
                    # Main menu button reset
                    self.buttons["start"].text = "Start Game - VS CPU"
                    self.buttons["sound"].text = "Sound - ON" if self.sound_on else "Sound - OFF"
                    break

            # Animations for loser winner text
            scale = 1 + 0.1 * math.sin(counter * 0.1)
            font_size = int(60 * scale)
            anim_font = pygame.font.SysFont("Arial", font_size)
            text_surf = anim_font.render(message, True, ACCENT)
            text_rect = text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))

            self.screen.fill(DARKGRAY)
            self.screen.blit(text_surf, text_rect)
            pygame.display.flip()

if __name__ == "__main__":
    app = App()
    app.run()
