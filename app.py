import pygame
import random
import sys
from pygame.math import Vector2

# Initialize
pygame.init()
pygame.mixer.init()

# Screen
WIDTH, HEIGHT = 400, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird Advanced")

# Game constants
FPS = 60
GRAVITY = 0.4
JUMP_STRENGTH = -8
PIPE_GAP = 200
PIPE_SPEED = 4
PIPE_FREQUENCY = 1500

# Colors & fonts
BACKGROUND_COLOR = (135, 206, 250)
PIPE_COLOR = (34, 139, 34)
FONT = pygame.font.SysFont("Arial", 32)

# Load sounds
JUMP_SOUND = pygame.mixer.Sound("jump.wav")

# Bird animation frames (flapping effect)
BIRD_FRAMES = []
for offset in [0, 3, -3]:
    surf = pygame.Surface((40, 30), pygame.SRCALPHA)
    pygame.draw.ellipse(surf, (255, 255, 0), (0, 5 + offset, 30, 20))
    pygame.draw.circle(surf, (255, 0, 0), (30, 15), 6)
    pygame.draw.circle(surf, (255, 255, 255), (32, 13), 3)
    pygame.draw.circle(surf, (0, 0, 0), (32, 13), 1)
    pygame.draw.polygon(surf, (255, 165, 0), [(35, 15), (40, 13), (40, 17)])
    BIRD_FRAMES.append(surf)

# Restart icon
RESTART_IMG = pygame.Surface((60, 60), pygame.SRCALPHA)
pygame.draw.circle(RESTART_IMG, (255, 255, 255), (30, 30), 30, 4)
pygame.draw.polygon(RESTART_IMG, (255, 255, 255), [(15, 30), (30, 15), (30, 45)])

clock = pygame.time.Clock()
high_score = 0


class Bird(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.frames = BIRD_FRAMES
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.original = self.image
        self.rect = self.image.get_rect(center=(100, HEIGHT // 2))
        self.pos = Vector2(self.rect.topleft)
        self.velocity = 0
        self.animation_timer = 0

    def update(self):
        self.velocity += GRAVITY
        self.pos.y += self.velocity
        self.rect.y = int(self.pos.y)

        # Animate flapping (speed tied to velocity)
        flap_speed = max(4, int(10 - abs(self.velocity)))
        self.animation_timer += 1
        if self.animation_timer >= flap_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)

        # Rotation based on velocity
        angle = -self.velocity * 3
        angle = max(-30, min(angle, 30))
        self.original = self.frames[self.frame_index]
        self.image = pygame.transform.rotate(self.original, angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def jump(self):
        self.velocity = JUMP_STRENGTH
        JUMP_SOUND.play()


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, height, is_top):
        super().__init__()
        self.image = pygame.Surface((60, height))
        self.image.fill(PIPE_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = 0 if is_top else HEIGHT - height
        self.passed = False  # for scoring

    def update(self):
        self.rect.x -= PIPE_SPEED
        if self.rect.right < 0:
            self.kill()


def spawn_pipes(pipes):
    gap_y = random.randint(150, HEIGHT - 150)
    top_height = gap_y - PIPE_GAP // 2
    bottom_height = HEIGHT - (gap_y + PIPE_GAP // 2)
    top_pipe = Pipe(WIDTH, top_height, True)
    bottom_pipe = Pipe(WIDTH, bottom_height, False)
    bottom_pipe.rect.top = gap_y + PIPE_GAP // 2
    pipes.add(top_pipe, bottom_pipe)


def show_text(text, y, size=32, color=(255, 255, 255)):
    font = pygame.font.SysFont("Arial", size)
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(WIDTH // 2, y))
    WIN.blit(surf, rect)


def start_menu():
    WIN.fill(BACKGROUND_COLOR)
    show_text("Flappy Bird", HEIGHT // 2 - 50, 48)
    show_text("Press SPACE to Start", HEIGHT // 2 + 20, 28)
    pygame.display.update()
    wait_for_space()


def wait_for_space():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return


def main():
    global high_score

    pygame.mixer.music.load("background.mp3")
    pygame.mixer.music.play(-1)

    bird = Bird()
    pipes = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group(bird)

    pygame.time.set_timer(pygame.USEREVENT, PIPE_FREQUENCY)
    score = 0
    running = True

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bird.jump()
            if event.type == pygame.USEREVENT:
                spawn_pipes(pipes)
                all_sprites.add(pipes)

        all_sprites.update()

        # Collision
        if pygame.sprite.spritecollideany(bird, pipes) or bird.rect.top < 0 or bird.rect.bottom > HEIGHT:
            running = False

        # Scoring
        for pipe in pipes:
            if not pipe.passed and pipe.rect.right < bird.rect.left:
                pipe.passed = True
                score += 0.5

        WIN.fill(BACKGROUND_COLOR)
        all_sprites.draw(WIN)
        show_text(f"Score: {int(score)}", 30)
        pygame.display.update()

    pygame.mixer.music.stop()
    high_score = max(high_score, int(score))
    game_over(int(score))


def game_over(score):
    WIN.fill(BACKGROUND_COLOR)
    show_text("Game Over", HEIGHT // 2 - 60, 40)
    show_text(f"Score: {score}", HEIGHT // 2 - 20, 32)
    show_text(f"High Score: {high_score}", HEIGHT // 2 + 20, 28)
    show_text("Press R to Restart", HEIGHT // 2 + 70, 26)
    WIN.blit(RESTART_IMG, RESTART_IMG.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 130)))
    pygame.display.update()
    wait_restart()


def wait_restart():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                main()


if __name__ == "__main__":
    start_menu()
    main()
