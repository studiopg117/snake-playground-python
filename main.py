import random
from dataclasses import dataclass

import pygame


HUD_HEIGHT = 80
GAME_WIDTH = 640
GAME_HEIGHT = 640
WINDOW_WIDTH = GAME_WIDTH
WINDOW_HEIGHT = HUD_HEIGHT + GAME_HEIGHT
CELL_SIZE = 20
GRID_WIDTH = GAME_WIDTH // CELL_SIZE
GRID_HEIGHT = GAME_HEIGHT // CELL_SIZE
BASE_FPS = 6
MAX_FPS = 20
FOODS_PER_LEVEL = 5

BACKGROUND_COLOR = (18, 18, 18)
GRID_COLOR = (32, 32, 32)
SNAKE_HEAD_COLOR = (80, 220, 120)
SNAKE_BODY_COLOR = (40, 170, 90)
FOOD_COLOR = (230, 70, 70)
TEXT_COLOR = (240, 240, 240)
HUD_BACKGROUND_COLOR = (28, 28, 28)
GAME_OVER_COLOR = (255, 210, 120)


@dataclass(frozen=True)
class Point:
    x: int
    y: int


class SnakeGame:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Snake Playground")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 24)
        self.large_font = pygame.font.SysFont("arial", 36)
        self.reset()

    def reset(self) -> None:
        center = Point(GRID_WIDTH // 2, GRID_HEIGHT // 2)
        self.snake = [
            center,
            Point(center.x - 1, center.y),
            Point(center.x - 2, center.y),
        ]
        self.direction = Point(1, 0)
        self.pending_direction = self.direction
        self.food = self.spawn_food()
        self.score = 0
        self.foods_eaten = 0
        self.game_over = False

    def spawn_food(self) -> Point:
        available_cells = [
            Point(x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if Point(x, y) not in self.snake
        ]
        return random.choice(available_cells)

    def get_level(self) -> int:
        return self.foods_eaten // FOODS_PER_LEVEL + 1

    def get_points_per_food(self) -> int:
        return self.get_level()

    def get_speed(self) -> int:
        return min(BASE_FPS + self.get_level() - 1, MAX_FPS)

    def handle_input(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if self.game_over and event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_r):
                    self.reset()
                    continue

                direction_map = {
                    pygame.K_UP: Point(0, -1),
                    pygame.K_DOWN: Point(0, 1),
                    pygame.K_LEFT: Point(-1, 0),
                    pygame.K_RIGHT: Point(1, 0),
                }

                if event.key in direction_map:
                    new_direction = direction_map[event.key]
                    # Prevent the snake from instantly reversing into itself.
                    if (
                        new_direction.x != -self.direction.x
                        or new_direction.y != -self.direction.y
                    ):
                        self.pending_direction = new_direction

        return True

    def update(self) -> None:
        if self.game_over:
            return

        self.direction = self.pending_direction
        head = self.snake[0]
        new_head = Point(
            (head.x + self.direction.x) % GRID_WIDTH,
            (head.y + self.direction.y) % GRID_HEIGHT,
        )

        if new_head in self.snake:
            self.game_over = True
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += self.get_points_per_food()
            self.foods_eaten += 1
            self.food = self.spawn_food()
        else:
            self.snake.pop()

    def draw_grid(self) -> None:
        pygame.draw.rect(self.screen, BACKGROUND_COLOR, (0, HUD_HEIGHT, GAME_WIDTH, GAME_HEIGHT))
        for x in range(0, WINDOW_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (x, HUD_HEIGHT), (x, WINDOW_HEIGHT))
        for y in range(HUD_HEIGHT, WINDOW_HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (WINDOW_WIDTH, y))

    def draw_snake(self) -> None:
        for index, segment in enumerate(self.snake):
            color = SNAKE_HEAD_COLOR if index == 0 else SNAKE_BODY_COLOR
            rect = pygame.Rect(
                segment.x * CELL_SIZE,
                HUD_HEIGHT + segment.y * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE,
            )
            pygame.draw.rect(self.screen, color, rect, border_radius=4)

    def draw_food(self) -> None:
        rect = pygame.Rect(
            self.food.x * CELL_SIZE,
            HUD_HEIGHT + self.food.y * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE,
        )
        pygame.draw.rect(self.screen, FOOD_COLOR, rect, border_radius=6)

    def draw_score(self) -> None:
        pygame.draw.rect(self.screen, HUD_BACKGROUND_COLOR, (0, 0, WINDOW_WIDTH, HUD_HEIGHT))
        pygame.draw.line(self.screen, GRID_COLOR, (0, HUD_HEIGHT - 1), (WINDOW_WIDTH, HUD_HEIGHT - 1))

        score_surface = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        level_surface = self.font.render(f"Level: {self.get_level()}", True, TEXT_COLOR)
        speed_surface = self.font.render(f"Speed: {self.get_speed()} FPS", True, TEXT_COLOR)

        self.screen.blit(score_surface, (16, 24))
        self.screen.blit(level_surface, (240, 24))
        self.screen.blit(speed_surface, (430, 24))

    def draw_game_over(self) -> None:
        overlay = pygame.Surface((WINDOW_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, HUD_HEIGHT))

        game_over_text = self.large_font.render("Game Over", True, GAME_OVER_COLOR)
        restart_text = self.font.render(
            "Press Enter, Space, or R to restart", True, TEXT_COLOR
        )

        game_center_y = HUD_HEIGHT + GAME_HEIGHT // 2
        game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, game_center_y - 20))
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, game_center_y + 24))
        self.screen.blit(game_over_text, game_over_rect)
        self.screen.blit(restart_text, restart_rect)

    def draw(self) -> None:
        self.screen.fill(BACKGROUND_COLOR)
        self.draw_grid()
        self.draw_food()
        self.draw_snake()
        self.draw_score()

        if self.game_over:
            self.draw_game_over()

        pygame.display.flip()

    def run(self) -> None:
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(self.get_speed())

        pygame.quit()


def main() -> None:
    game = SnakeGame()
    game.run()


if __name__ == "__main__":
    main()
