import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 80
BALL_SIZE = 15
PADDLE_SPEED = 6
BALL_SPEED = 5

# GitHub-style colors
COLORS = {
    'bg': (13, 17, 23),  # Dark GitHub background
    'grid': (22, 27, 34),  # Slightly lighter for grid
    'paddle': (48, 54, 61),  # GitHub gray
    'ball': (255, 255, 255),  # White ball
    'text': (201, 209, 217),  # GitHub text color
    'contribution_levels': [
        (22, 27, 34),    # No contributions
        (14, 68, 41),    # Low contributions
        (0, 109, 50),    # Medium-low
        (38, 166, 65),   # Medium
        (57, 211, 83)    # High contributions
    ]
}

class ContributionSquare:
    def __init__(self, x, y, size=8):
        self.x = x
        self.y = y
        self.size = size
        self.level = 0
        self.max_level = len(COLORS['contribution_levels']) - 1
        
    def increase_level(self):
        if self.level < self.max_level:
            self.level += 1
            
    def draw(self, screen):
        color = COLORS['contribution_levels'][self.level]
        pygame.draw.rect(screen, color, (self.x, self.y, self.size, self.size))
        # Add border like GitHub
        pygame.draw.rect(screen, COLORS['grid'], (self.x, self.y, self.size, self.size), 1)

class Paddle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.speed = PADDLE_SPEED
        
    def move_up(self):
        if self.y > 0:
            self.y -= self.speed
            
    def move_down(self):
        if self.y < WINDOW_HEIGHT - self.height:
            self.y += self.speed
            
    def draw(self, screen):
        # Draw paddle as a series of small squares (GitHub style)
        square_size = 8
        for i in range(0, self.height, square_size + 2):
            for j in range(0, self.width, square_size + 2):
                if i + square_size <= self.height and j + square_size <= self.width:
                    pygame.draw.rect(screen, COLORS['contribution_levels'][3], 
                                   (self.x + j, self.y + i, square_size, square_size))
                    pygame.draw.rect(screen, COLORS['grid'], 
                                   (self.x + j, self.y + i, square_size, square_size), 1)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = BALL_SIZE
        self.dx = random.choice([-BALL_SPEED, BALL_SPEED])
        self.dy = random.uniform(-BALL_SPEED, BALL_SPEED)
        
    def move(self):
        self.x += self.dx
        self.y += self.dy
        
        # Bounce off top and bottom walls
        if self.y <= 0 or self.y >= WINDOW_HEIGHT - self.size:
            self.dy = -self.dy
            
    def reset(self):
        self.x = WINDOW_WIDTH // 2
        self.y = WINDOW_HEIGHT // 2
        self.dx = random.choice([-BALL_SPEED, BALL_SPEED])
        self.dy = random.uniform(-BALL_SPEED, BALL_SPEED)
        
    def draw(self, screen):
        # Draw ball as a bright contribution square
        pygame.draw.rect(screen, COLORS['ball'], (self.x, self.y, self.size, self.size))
        pygame.draw.rect(screen, COLORS['contribution_levels'][4], 
                        (self.x, self.y, self.size, self.size), 2)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

class PongGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("GitHub Style Pong")
        self.clock = pygame.time.Clock()
        
        # Game objects
        self.left_paddle = Paddle(30, WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.right_paddle = Paddle(WINDOW_WIDTH - 30 - PADDLE_WIDTH, WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.ball = Ball(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        
        # Scores
        self.left_score = 0
        self.right_score = 0
        
        # Font for score display
        self.font = pygame.font.Font(None, 48)
        
        # Create contribution graph background
        self.contribution_squares = []
        square_size = 8
        spacing = 2
        for row in range(0, WINDOW_HEIGHT, square_size + spacing):
            for col in range(0, WINDOW_WIDTH, square_size + spacing):
                square = ContributionSquare(col, row, square_size)
                # Random initial contribution level
                square.level = random.choice([0, 0, 0, 1, 1, 2])
                self.contribution_squares.append(square)
    
    def handle_collisions(self):
        ball_rect = self.ball.get_rect()
        
        # Left paddle collision
        if ball_rect.colliderect(self.left_paddle.get_rect()) and self.ball.dx < 0:
            self.ball.dx = -self.ball.dx
            # Add some randomness to the angle
            self.ball.dy += random.uniform(-1, 1)
            self.add_contribution_effect(self.left_paddle.x, self.left_paddle.y)
            
        # Right paddle collision
        if ball_rect.colliderect(self.right_paddle.get_rect()) and self.ball.dx > 0:
            self.ball.dx = -self.ball.dx
            # Add some randomness to the angle
            self.ball.dy += random.uniform(-1, 1)
            self.add_contribution_effect(self.right_paddle.x, self.right_paddle.y)
    
    def add_contribution_effect(self, x, y):
        # Light up nearby contribution squares when ball hits paddle
        for square in self.contribution_squares:
            distance = math.sqrt((square.x - x) ** 2 + (square.y - y) ** 2)
            if distance < 50:  # Effect radius
                square.increase_level()
    
    def check_scoring(self):
        if self.ball.x < 0:
            self.right_score += 1
            self.ball.reset()
            self.add_score_effect()
            
        elif self.ball.x > WINDOW_WIDTH:
            self.left_score += 1
            self.ball.reset()
            self.add_score_effect()
    
    def add_score_effect(self):
        # Light up random squares when someone scores
        for _ in range(20):
            square = random.choice(self.contribution_squares)
            square.increase_level()
    
    def draw_ui(self):
        # Draw scores with GitHub style
        left_score_text = self.font.render(str(self.left_score), True, COLORS['text'])
        right_score_text = self.font.render(str(self.right_score), True, COLORS['text'])
        
        self.screen.blit(left_score_text, (WINDOW_WIDTH // 4, 50))
        self.screen.blit(right_score_text, (3 * WINDOW_WIDTH // 4, 50))
        
        # Draw center line as contribution squares
        for y in range(0, WINDOW_HEIGHT, 20):
            pygame.draw.rect(self.screen, COLORS['contribution_levels'][1], 
                           (WINDOW_WIDTH // 2 - 4, y, 8, 8))
    
    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        # Left paddle (W/S keys)
        if keys[pygame.K_w]:
            self.left_paddle.move_up()
        if keys[pygame.K_s]:
            self.left_paddle.move_down()
            
        # Right paddle (UP/DOWN arrows)
        if keys[pygame.K_UP]:
            self.right_paddle.move_up()
        if keys[pygame.K_DOWN]:
            self.right_paddle.move_down()
    
    def run(self):
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        # Reset game
                        self.left_score = 0
                        self.right_score = 0
                        self.ball.reset()
                        # Reset contribution squares
                        for square in self.contribution_squares:
                            square.level = random.choice([0, 0, 0, 1, 1, 2])
            
            # Handle input
            self.handle_input()
            
            # Update game objects
            self.ball.move()
            self.handle_collisions()
            self.check_scoring()
            
            # Draw everything
            self.screen.fill(COLORS['bg'])
            
            # Draw contribution graph background
            for square in self.contribution_squares:
                square.draw(self.screen)
            
            # Draw game objects
            self.left_paddle.draw(self.screen)
            self.right_paddle.draw(self.screen)
            self.ball.draw(self.screen)
            
            # Draw UI
            self.draw_ui()
            
            # Add instructions
            instruction_font = pygame.font.Font(None, 24)
            instructions = [
                "Left Player: W/S keys",
                "Right Player: UP/DOWN arrows",
                "Press R to reset game"
            ]
            
            for i, instruction in enumerate(instructions):
                text = instruction_font.render(instruction, True, COLORS['text'])
                self.screen.blit(text, (10, WINDOW_HEIGHT - 80 + i * 25))
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    game = PongGame()
    game.run()