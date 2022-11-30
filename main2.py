import pygame
import random
from pygame import Rect
from pygame.sprite import Sprite

class World():
    def __init__(self,WIDTH,HEIGHT,SCALE):
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.SCALE = SCALE
        self.display = pygame.display.set_mode((SCALE * WIDTH, SCALE * HEIGHT))
        self.food = Food((random.randrange(WIDTH), random.randrange(HEIGHT)))
        self.snakes = []

    def addSnake(self,snake):
        self.snakes.append(snake)

    def spawnNewFood(self):
        self.food.newPosition((random.randrange(WIDTH), random.randrange(HEIGHT)))

    def drawFood(self):
        pygame.draw.rect(self.display, "green", (self.SCALE * self.food.position[0], self.SCALE * self.food.position[1], self.SCALE, self.SCALE))

    def drawSnake(self):
        for snake in self.snakes:
            if snake.running:
                for x, y in snake.body:
                    pygame.draw.rect(self.display, "red", (self.SCALE * x, self.SCALE * y, self.SCALE, self.SCALE))

                    if self.food.position == (x, y):
                        snake.grow()
                        ev = pygame.event.Event(GAME_EVENT, {'txt': "mmmnhami"})
                        pygame.event.post(ev)
                        print("Sent")
                        ev = pygame.event.Event(GAME_EVENT, {'txt': "dammmm"})
                        pygame.event.post(ev)
                        self.spawnNewFood()

                    if x not in range(self.WIDTH) or y not in range(self.HEIGHT):
                        print("Snake crashed against the wall")
                        snake.dead()

                    if snake.body.count((x, y)) > 1:
                        print("Snake eats self")
                        snake.dead()

                snake.move()
            else:
                for x, y in snake.body:
                    pygame.draw.rect(self.display, "green", (self.SCALE * x, self.SCALE * y, self.SCALE, self.SCALE))


    def drawWorld(self):
        self.display.fill("white")
        self.drawFood()
        self.drawSnake()

    def allDead(self):
        return any([snake.running for snake in self.snakes])

    def killAll(self):
        [snake.dead() for snake in self.snakes]

class Food(Sprite):
    def __init__(self, position):
        Sprite.__init__(self)
        self.position = position

    def newPosition(self,position):
        self.position = position

class Snake(Sprite):
    def __init__(self,snake_body: list, snake_direction):
        Sprite.__init__(self)
        self.length = len(snake_body)
        self.body = snake_body
        self.direction = snake_direction
        self.running = True

    def grow(self):
        self.length += 1

    def changeDirection(self,direction):
        if not ((direction[0]*-1) == self.direction[0] and (direction[1]*-1) == self.direction[1]):
            self.direction = direction

    def dead(self):
        self.running = False

    def move(self):
        # move snake
        self.body[0:0] = [
            (self.body[0][0] + self.direction[0], self.body[0][1] + self.direction[1])
        ]
        while len(self.body) > self.length:
            self.body.pop()

class Command:
    def execute(snakes):
        raise NotImplemented

class Up(Command):
    def execute(snakes):
        snakes[0].changeDirection((0,-1))
class Down(Command):
    def execute(snakes):
        snakes[0].changeDirection((0,1))
class Left(Command):
    def execute(snakes):
        snakes[0].changeDirection((-1,0))
class Right(Command):
    def execute(snakes):
        snakes[0].changeDirection((1,0))

class W(Command):
    def execute(snakes):
        snakes[1].changeDirection((0,-1))
class S(Command):
    def execute(snakes):
        snakes[1].changeDirection((0,1))
class A(Command):
    def execute(snakes):
        snakes[1].changeDirection((-1,0))
class D(Command):
    def execute(snakes):
        snakes[1].changeDirection((1,0))

class InputHandler:
    command = {
        pygame.K_UP: Up,
        pygame.K_DOWN: Down,
        pygame.K_LEFT: Left,
        pygame.K_RIGHT: Right,
        pygame.K_w: W,
        pygame.K_s: S,
        pygame.K_a: A,
        pygame.K_d: D
    }

    def handleInput():
        return InputHandler.command[event.key]
class Die:
    def kill_snake(snake):
        snake.dead()

class EventHandler:
    def __init__(self):
        self.events = {}
    def register(self,event,event_handler):
        try:
            self.events[event].append(event_handler)
        except:
            self.events[event] = [event_handler]
    def notify(self,entity, event):
        for event_handler in self.events[event]:
            event_handler(entity)
class Physics(EventHandler)
    def __init__(self):
        super().__init__()
    def update_entity(self,entity):
        ´pass

WIDTH = 80
HEIGHT = 40
SCALE = 10
world = World(WIDTH,HEIGHT,SCALE)
clock = pygame.time.Clock()

snakes = [Snake([(40, 20-x*2), (39, 20-x*2), (38, 20-x*2)],(1,0)) for x in range(2)]

for snake in snakes:
    world.addSnake(snake)

GAME_EVENT = pygame.event.custom_type()
command = Right

while world.allDead():
    for event in pygame.event.get():
        if event == pygame.QUIT:
            world.killAll()
        elif event == GAME_EVENT:
            print(event.txt)
        elif event.type == pygame.KEYDOWN:
            command = InputHandler.handleInput()
            command.execute(snakes)

    world.drawWorld()

    # update window
    pygame.display.flip()
    clock.tick(15)

pygame.quit()