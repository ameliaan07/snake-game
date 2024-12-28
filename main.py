import pygame
import random
import sys
from enum import Enum
from collections import deque
import asyncio
import platform

# 检查是否在web环境中运行
is_web = platform.system() == 'Emscripten'

# 游戏设置
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE
GAME_SPEED = 5

# 颜色定义
class Colors:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    DARK_GREEN = (0, 200, 0)
    LIGHT_GREEN = (150, 255, 150)
    GRID_COLOR = (40, 40, 40)
    SNAKE_GRADIENT = [
        (0, 255, 0),    # 头部颜色
        (50, 255, 50),  # 身体渐变色
        (100, 255, 100),
        (150, 255, 150)
    ]

class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

class Snake:
    def __init__(self):
        self.body = deque([(GRID_WIDTH // 2, GRID_HEIGHT // 2)])
        self.direction = Direction.RIGHT
        self.grow = False

    def move(self):
        head = self.body[0]
        if self.direction == Direction.UP:
            new_head = (head[0], head[1] - 1)
        elif self.direction == Direction.DOWN:
            new_head = (head[0], head[1] + 1)
        elif self.direction == Direction.LEFT:
            new_head = (head[0] - 1, head[1])
        else:
            new_head = (head[0] + 1, head[1])

        self.body.appendleft(new_head)
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False

    def change_direction(self, new_direction):
        opposite_directions = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }
        if new_direction != opposite_directions.get(self.direction):
            self.direction = new_direction

class Game:
    def __init__(self):
        self.screen = None
        self.clock = pygame.time.Clock()
        self.reset_game()

    def reset_game(self):
        self.snake = Snake()
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False
        self.running = True

    async def initialize(self):
        """异步初始化游戏"""
        try:
            pygame.init()
            # 使用最基本的显示模式
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
            return True
        except Exception as e:
            print(f"Initialization error: {e}")
            return False

    def generate_food(self):
        while True:
            food = (random.randint(0, GRID_WIDTH - 1),
                   random.randint(0, GRID_HEIGHT - 1))
            if food not in self.snake.body:
                return food

    def check_collision(self):
        head = self.snake.body[0]
        return (head[0] < 0 or head[0] >= GRID_WIDTH or
                head[1] < 0 or head[1] >= GRID_HEIGHT or
                head in list(self.snake.body)[1:])

    def draw(self):
        if not self.screen:
            return
            
        self.screen.fill(Colors.BLACK)
        
        # 绘制网格
        for x in range(0, WINDOW_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, Colors.GRID_COLOR, (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, Colors.GRID_COLOR, (0, y), (WINDOW_WIDTH, y))
        
        # 绘制蛇
        snake_length = len(self.snake.body)
        for i, segment in enumerate(self.snake.body):
            x = segment[0] * GRID_SIZE
            y = segment[1] * GRID_SIZE
            
            if i == 0:  # 蛇头
                # 绘制圆形蛇头
                center = (x + GRID_SIZE // 2, y + GRID_SIZE // 2)
                pygame.draw.circle(self.screen, Colors.DARK_GREEN, center, GRID_SIZE // 2 - 1)
                
                # 添加眼睛
                eye_color = Colors.WHITE
                eye_radius = GRID_SIZE // 8
                eye_offset = GRID_SIZE // 4
                
                # 根据方向调整眼睛位置
                if self.snake.direction == Direction.RIGHT:
                    left_eye = (x + GRID_SIZE - eye_offset, y + eye_offset)
                    right_eye = (x + GRID_SIZE - eye_offset, y + GRID_SIZE - eye_offset)
                elif self.snake.direction == Direction.LEFT:
                    left_eye = (x + eye_offset, y + eye_offset)
                    right_eye = (x + eye_offset, y + GRID_SIZE - eye_offset)
                elif self.snake.direction == Direction.UP:
                    left_eye = (x + eye_offset, y + eye_offset)
                    right_eye = (x + GRID_SIZE - eye_offset, y + eye_offset)
                else:  # DOWN
                    left_eye = (x + eye_offset, y + GRID_SIZE - eye_offset)
                    right_eye = (x + GRID_SIZE - eye_offset, y + GRID_SIZE - eye_offset)
                
                pygame.draw.circle(self.screen, eye_color, left_eye, eye_radius)
                pygame.draw.circle(self.screen, eye_color, right_eye, eye_radius)
                
            else:  # 蛇身
                # 创建渐变效果
                color_index = min(i, len(Colors.SNAKE_GRADIENT) - 1)
                color = Colors.SNAKE_GRADIENT[color_index]
                
                # 绘制圆角矩形作为身体段
                rect = pygame.Rect(x + 1, y + 1, GRID_SIZE - 2, GRID_SIZE - 2)
                pygame.draw.rect(self.screen, color, rect, border_radius=GRID_SIZE // 4)
                
                # 添加光晕效果
                if i < snake_length - 1:
                    next_segment = self.snake.body[i + 1]
                    mid_x = (segment[0] + next_segment[0]) * GRID_SIZE // 2
                    mid_y = (segment[1] + next_segment[1]) * GRID_SIZE // 2
                    pygame.draw.circle(self.screen, color, (mid_x + GRID_SIZE//2, mid_y + GRID_SIZE//2), 
                                     GRID_SIZE // 3)
        
        # 绘制食物（苹果样式）
        x = self.food[0] * GRID_SIZE
        y = self.food[1] * GRID_SIZE
        apple_color = Colors.RED
        
        # 主体
        center = (x + GRID_SIZE // 2, y + GRID_SIZE // 2)
        pygame.draw.circle(self.screen, apple_color, center, GRID_SIZE // 2 - 2)
        
        # 叶子
        leaf_color = (0, 180, 0)
        leaf_points = [
            (x + GRID_SIZE//2, y + 2),
            (x + GRID_SIZE//2 + 4, y - 2),
            (x + GRID_SIZE//2 + 2, y + 3)
        ]
        pygame.draw.polygon(self.screen, leaf_color, leaf_points)
        
        # 绘制分数
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, Colors.WHITE)
        self.screen.blit(score_text, (10, 10))
        
        if self.game_over:
            # 创建半透明遮罩
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(128)
            self.screen.blit(overlay, (0, 0))
            
            # 游戏结束文本
            game_over_text = font.render('Game Over! Press R to Restart', True, Colors.WHITE)
            text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
            self.screen.blit(game_over_text, text_rect)
        
        pygame.display.flip()

    def handle_keydown(self, key):
        if self.game_over:
            if key == pygame.K_r:
                self.reset_game()
        else:
            if key == pygame.K_UP:
                self.snake.change_direction(Direction.UP)
            elif key == pygame.K_DOWN:
                self.snake.change_direction(Direction.DOWN)
            elif key == pygame.K_LEFT:
                self.snake.change_direction(Direction.LEFT)
            elif key == pygame.K_RIGHT:
                self.snake.change_direction(Direction.RIGHT)

    def update(self):
        if not self.game_over:
            self.snake.move()
            if self.snake.body[0] == self.food:
                self.snake.grow = True
                self.food = self.generate_food()
                self.score += 10
            if self.check_collision():
                self.game_over = True

    async def run(self):
        if not await self.initialize():
            return

        try:
            while self.running:
                if is_web:
                    await asyncio.sleep(0.016)
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.KEYDOWN:
                        self.handle_keydown(event.key)

                if self.running:
                    self.update()
                    self.draw()
                    self.clock.tick(GAME_SPEED)
                    
        except Exception as e:
            print(f"Game error: {e}")
            import traceback
            traceback.print_exc()

async def async_init():
    """异步初始化"""
    try:
        pygame.init()
        if is_web:
            print("Starting initialization...")
            # 减少等待时间
            await asyncio.sleep(0.05)  # 从 0.1 改为 0.05
            
            # 使用最基本的显示模式
            screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
            return screen
    except Exception as e:
        print(f"Initialization error: {e}")
        return None

async def main():
    try:
        game = Game()
        await game.run()
    except Exception as e:
        print(f"Main error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if not is_web:
            pygame.quit()
            sys.exit()

if __name__ == '__main__':
    asyncio.run(main()) 