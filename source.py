import pygame
import time
import random
import os
from pygame.locals import *

size = 40  # size of one block
HIGHSCORE_FILE = "highscore.txt"

class Apple:
    def __init__(self, parentScreen):
        self.parentScreen = parentScreen
        self.image = pygame.image.load("SnakeApple/resources/apple.jpg").convert()
        self.move()

    def draw(self):
        self.parentScreen.blit(self.image, (self.x, self.y))

    def move(self):
        self.x = random.randint(1, 19) * size  # Random x position
        self.y = random.randint(1, 14) * size  # Random y position

class Snake:
    def __init__(self, surface, length):
        self.parentScreen = surface
        self.block = pygame.image.load("SnakeApple/resources/block.jpg").convert()
        
        self.length = length
        self.x = [size] * length
        self.y = [size] * length

        self.direction = 'down'

    def increaseLength(self):
        self.length += 1
        self.x.append(-1)
        self.y.append(-1)    

    def move_up(self):
        if self.direction != 'down':  # Prevent reverse direction
            self.direction = 'up'

    def move_down(self):
        if self.direction != 'up':  # Prevent reverse direction
            self.direction = 'down'

    def move_left(self):
        if self.direction != 'right':  # Prevent reverse direction
            self.direction = 'left'

    def move_right(self):
        if self.direction != 'left':  # Prevent reverse direction
            self.direction = 'right'

    def draw(self):
        for i in range(self.length):
            self.parentScreen.blit(self.block, (self.x[i], self.y[i]))
        pygame.display.flip()

    def walk(self):
        for i in range(self.length - 1, 0, -1):
            self.x[i] = self.x[i - 1]
            self.y[i] = self.y[i - 1]
        if self.direction == 'left':
            self.x[0] -= size
        elif self.direction == 'right':
            self.x[0] += size
        elif self.direction == 'up':
            self.y[0] -= size
        elif self.direction == 'down':
            self.y[0] += size
        self.draw()

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.surface = pygame.display.set_mode((800, 600))
        self.background = pygame.image.load("SnakeApple/resources/background.jpg").convert()
        self.playBackGround()
        self.snake = Snake(self.surface, 2)
        self.apples = [Apple(self.surface) for _ in range(3)]  # Create apples
        self.base_speed = 0.2  # Initial speed
        self.high_score = self.load_high_score()

    def load_high_score(self):
        if os.path.exists(HIGHSCORE_FILE):
            with open(HIGHSCORE_FILE, "r") as file:
                return int(file.read())
        return 0

    def save_high_score(self):
        with open(HIGHSCORE_FILE, "w") as file:
            file.write(str(self.high_score))

    def reset(self):
        self.snake = Snake(self.surface, 2)
        self.apples = [Apple(self.surface) for _ in range(3)]  # Reset apples

    def displayScore(self):
        font = pygame.font.SysFont('arial', 30)
        score = font.render(f"Score: {self.snake.length}", True, (200, 200, 200))
        self.surface.blit(score, (660, 20))
        high_score = font.render(f"High Score: {self.high_score}", True, (200, 200, 200))
        self.surface.blit(high_score, (560, 60))
        pygame.display.flip()

    def playBackGround(self):
        pygame.mixer.music.load("SnakeApple/resources/bg_music_1.mp3")
        pygame.mixer.music.play(-1, 0)  # Play endlessly from the beginning

    def playSound(self, sound):
        if sound == "ding":
            sound = pygame.mixer.Sound("SnakeApple/resources/ding.mp3")
            pygame.mixer.Sound.play(sound)
        elif sound == "crash":
            sound = pygame.mixer.Sound("SnakeApple/resources/crash.mp3")
            pygame.mixer.Sound.play(sound)

    def showGameOver(self):
        font = pygame.font.SysFont('arial', 40)
        line1 = font.render(f"GAME OVER !!\nScore: {self.snake.length}", True, (200, 200, 200))
        self.surface.blit(line1, (200, 100))
        line2 = font.render("To play again Press Enter, else ESC", True, (200, 200, 200))
        self.surface.blit(line2, (100, 200))
        if self.snake.length > self.high_score:
            self.high_score = self.snake.length
            self.save_high_score()
        pygame.display.flip()
        pygame.mixer.music.pause()

    def renderBackGround(self):
        self.surface.blit(self.background, (0, 0))

    def play(self):
        self.renderBackGround()
        self.snake.walk()
        for apple in self.apples:
            apple.draw()
        self.displayScore()
        pygame.display.flip()

        # Snake colliding with any apple
        for apple in self.apples:
            if self.isCollision(self.snake.x[0], self.snake.y[0], apple.x, apple.y):
                self.playSound("ding")
                self.snake.increaseLength()
                apple.move()

        # Snake colliding with itself
        for i in range(1, self.snake.length):  # Start loop from 1 instead of 2 to prevent early collision
            if self.isCollision(self.snake.x[0], self.snake.y[0], self.snake.x[i], self.snake.y[i]):
                self.playSound("crash")
                raise Exception("Game Over")

        # Snake colliding with boundary
        if self.snake.x[0] < 0 or self.snake.x[0] >= 800 or self.snake.y[0] < 0 or self.snake.y[0] >= 600:
            self.playSound("crash")
            raise Exception("Game Over")

    def isCollision(self, x1, y1, x2, y2):
        return x1 == x2 and y1 == y2

    def run(self):
        running = True
        pause = False

        while running:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    if event.key == K_RETURN:
                        pygame.mixer.music.unpause()
                        pause = False
                    if not pause:
                        if event.key == K_UP:
                            self.snake.move_up()
                        if event.key == K_DOWN:
                            self.snake.move_down()
                        if event.key == K_LEFT:
                            self.snake.move_left()
                        if event.key == K_RIGHT:
                            self.snake.move_right()
                elif event.type == QUIT:
                    running = False

            try:
                if not pause:
                    self.play()
                    sleep_time = self.base_speed - (self.snake.length // 10) * 0.02  # Increase speed based on score
                    sleep_time = max(0.05, sleep_time)  # Ensure sleep time doesn't go below 0.05
                    time.sleep(sleep_time)
            except Exception as e:
                self.showGameOver()
                pause = True
                self.reset()
                time.sleep(1)  # Reduced the sleep time after game over

if __name__ == '__main__':
    game = Game()
    game.run()



"""
random.ra
"""