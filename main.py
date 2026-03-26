import json
import random
from dataclasses import dataclass
from pathlib import Path

import pygame


HUD_HEIGHT = 40
GAME_WIDTH = 320
GAME_HEIGHT = 320
WINDOW_WIDTH = GAME_WIDTH
WINDOW_HEIGHT = HUD_HEIGHT + GAME_HEIGHT
CELL_SIZE = 20
GRID_WIDTH = GAME_WIDTH // CELL_SIZE
GRID_HEIGHT = GAME_HEIGHT // CELL_SIZE
BASE_FPS = 6
MAX_FPS = 20
MENU_FPS = 30
FOODS_PER_LEVEL = 5
MAX_HIGH_SCORES = 5
MAX_NAME_LENGTH = 10
SCORE_FILE = Path("data/high_scores.json")

BACKGROUND_COLOR = (18, 18, 18)
GRID_COLOR = (32, 32, 32)
SNAKE_HEAD_COLOR = (80, 220, 120)
SNAKE_BODY_COLOR = (40, 170, 90)
FOOD_COLOR = (230, 70, 70)
TEXT_COLOR = (240, 240, 240)
HUD_BACKGROUND_COLOR = (28, 28, 28)
GAME_OVER_COLOR = (255, 210, 120)
ACCENT_COLOR = (90, 180, 255)
MUTED_TEXT_COLOR = (190, 190, 190)
BUTTON_COLOR = (38, 38, 38)
BUTTON_HOVER_COLOR = (52, 52, 52)
MENU_GRADIENT_TOP = (10, 30, 58)
MENU_GRADIENT_BOTTOM = (8, 12, 22)
MENU_PANEL_COLOR = (12, 20, 35, 210)
MENU_TITLE_PANEL_COLOR = (16, 28, 48, 220)

STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_SCORES = "scores"
STATE_NAME_ENTRY = "name_entry"


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
        self.font = pygame.font.SysFont("arial", 20)
        self.large_font = pygame.font.SysFont("arial", 28)
        self.title_font = pygame.font.SysFont("arial", 34, bold=True)
        self.small_font = pygame.font.SysFont("arial", 16)
        self.menu_options = ["Start Game", "High Scores", "Quit"]
        self.menu_index = 0
        self.menu_hover_index = -1
        self.state = STATE_MENU
        self.high_scores = self.load_high_scores()
        self.pending_high_score = False
        self.name_input = ""
        self.caret_visible = True
        self.caret_blink_ms = 500
        self.next_caret_toggle_ms = pygame.time.get_ticks() + self.caret_blink_ms
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
        self.pending_high_score = False
        self.name_input = ""
        self.caret_visible = True
        self.next_caret_toggle_ms = pygame.time.get_ticks() + self.caret_blink_ms

    def start_game(self) -> None:
        self.reset()
        self.state = STATE_PLAYING

    def spawn_food(self) -> Point:
        available_cells = [
            Point(x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if Point(x, y) not in self.snake
        ]
        return random.choice(available_cells)

    def default_high_scores(self) -> list[dict[str, int | str]]:
        return [{"name": "Player", "score": 0} for _ in range(MAX_HIGH_SCORES)]

    def normalize_score_entry(self, entry: object) -> dict[str, int | str] | None:
        if isinstance(entry, dict):
            name = str(entry.get("name", "Player")).strip() or "Player"
            score = entry.get("score", 0)
            if isinstance(score, (int, float)):
                return {"name": name[:MAX_NAME_LENGTH], "score": int(score)}
            return None

        if isinstance(entry, (int, float)):
            return {"name": "Player", "score": int(entry)}

        return None

    def load_high_scores(self) -> list[dict[str, int | str]]:
        default_scores = self.default_high_scores()
        SCORE_FILE.parent.mkdir(parents=True, exist_ok=True)

        if not SCORE_FILE.exists():
            self.save_high_scores(default_scores)
            return default_scores

        try:
            data = json.loads(SCORE_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            self.save_high_scores(default_scores)
            return default_scores

        if not isinstance(data, list):
            self.save_high_scores(default_scores)
            return default_scores

        cleaned_scores = []
        for item in data:
            normalized = self.normalize_score_entry(item)
            if normalized is not None:
                cleaned_scores.append(normalized)

        cleaned_scores.sort(key=lambda item: int(item["score"]), reverse=True)
        cleaned_scores = cleaned_scores[:MAX_HIGH_SCORES]
        while len(cleaned_scores) < MAX_HIGH_SCORES:
            cleaned_scores.append({"name": "Player", "score": 0})

        self.save_high_scores(cleaned_scores)
        return cleaned_scores

    def save_high_scores(self, scores: list[dict[str, int | str]]) -> None:
        SCORE_FILE.parent.mkdir(parents=True, exist_ok=True)
        SCORE_FILE.write_text(json.dumps(scores, indent=2), encoding="utf-8")

    def is_high_score(self, score: int) -> bool:
        lowest_score = int(self.high_scores[-1]["score"])
        return score > 0 and score > lowest_score

    def submit_high_score(self) -> None:
        name = self.name_input.strip() or "Player"
        entry = {"name": name[:MAX_NAME_LENGTH], "score": self.score}
        updated_scores = self.high_scores + [entry]
        updated_scores.sort(key=lambda item: int(item["score"]), reverse=True)
        self.high_scores = updated_scores[:MAX_HIGH_SCORES]
        self.save_high_scores(self.high_scores)
        self.pending_high_score = False
        self.name_input = ""
        self.state = STATE_SCORES

    def get_level(self) -> int:
        return self.foods_eaten // FOODS_PER_LEVEL + 1

    def get_points_per_food(self) -> int:
        return self.get_level()

    def get_speed(self) -> int:
        return min(BASE_FPS + self.get_level() - 1, MAX_FPS)

    def get_menu_option_rects(self) -> list[pygame.Rect]:
        rects = []
        width = 220
        height = 42
        left = (WINDOW_WIDTH - width) // 2
        for index, _ in enumerate(self.menu_options):
            top = 168 + index * 52
            rects.append(pygame.Rect(left, top, width, height))
        return rects

    def activate_menu_option(self, index: int) -> bool:
        self.menu_index = index
        selected = self.menu_options[index]
        if selected == "Start Game":
            self.start_game()
        elif selected == "High Scores":
            self.state = STATE_SCORES
        elif selected == "Quit":
            return False
        return True

    def handle_menu_input(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.menu_index = (self.menu_index - 1) % len(self.menu_options)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.menu_index = (self.menu_index + 1) % len(self.menu_options)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self.activate_menu_option(self.menu_index)
        elif event.type == pygame.MOUSEMOTION:
            self.menu_hover_index = -1
            for index, rect in enumerate(self.get_menu_option_rects()):
                if rect.collidepoint(event.pos):
                    self.menu_hover_index = index
                    self.menu_index = index
                    break
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for index, rect in enumerate(self.get_menu_option_rects()):
                if rect.collidepoint(event.pos):
                    return self.activate_menu_option(index)
        return True

    def handle_scores_input(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.KEYDOWN and event.key in (
            pygame.K_ESCAPE,
            pygame.K_BACKSPACE,
            pygame.K_RETURN,
            pygame.K_SPACE,
        ):
            self.state = STATE_MENU
        return True

    def handle_name_entry_input(self, event: pygame.event.Event) -> bool:
        if event.type != pygame.KEYDOWN:
            return True

        if event.key == pygame.K_RETURN:
            self.submit_high_score()
        elif event.key == pygame.K_ESCAPE:
            self.submit_high_score()
        elif event.key == pygame.K_BACKSPACE:
            self.name_input = self.name_input[:-1]
        else:
            if event.unicode and event.unicode.isprintable():
                if len(self.name_input) < MAX_NAME_LENGTH:
                    self.name_input += event.unicode

        self.caret_visible = True
        self.next_caret_toggle_ms = pygame.time.get_ticks() + self.caret_blink_ms
        return True

    def handle_playing_input(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        if self.game_over:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_r):
                self.start_game()
            elif event.key in (pygame.K_ESCAPE, pygame.K_m):
                self.state = STATE_MENU
            return

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

    def handle_input(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if self.state == STATE_MENU:
                if not self.handle_menu_input(event):
                    return False
            elif self.state == STATE_SCORES:
                if not self.handle_scores_input(event):
                    return False
            elif self.state == STATE_NAME_ENTRY:
                if not self.handle_name_entry_input(event):
                    return False
            elif self.state == STATE_PLAYING:
                self.handle_playing_input(event)

        return True

    def update(self) -> None:
        if self.state == STATE_NAME_ENTRY:
            now = pygame.time.get_ticks()
            if now >= self.next_caret_toggle_ms:
                self.caret_visible = not self.caret_visible
                self.next_caret_toggle_ms = now + self.caret_blink_ms
            return

        if self.state != STATE_PLAYING or self.game_over:
            return

        self.direction = self.pending_direction
        head = self.snake[0]
        new_head = Point(
            (head.x + self.direction.x) % GRID_WIDTH,
            (head.y + self.direction.y) % GRID_HEIGHT,
        )

        if new_head in self.snake:
            self.game_over = True
            if self.is_high_score(self.score):
                self.pending_high_score = True
                self.name_input = ""
                self.caret_visible = True
                self.next_caret_toggle_ms = pygame.time.get_ticks() + self.caret_blink_ms
                self.state = STATE_NAME_ENTRY
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += self.get_points_per_food()
            self.foods_eaten += 1
            self.food = self.spawn_food()
        else:
            self.snake.pop()

    def draw_grid(self) -> None:
        pygame.draw.rect(
            self.screen, BACKGROUND_COLOR, (0, HUD_HEIGHT, GAME_WIDTH, GAME_HEIGHT)
        )
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

    def draw_hud(self) -> None:
        pygame.draw.rect(self.screen, HUD_BACKGROUND_COLOR, (0, 0, WINDOW_WIDTH, HUD_HEIGHT))
        pygame.draw.line(
            self.screen, GRID_COLOR, (0, HUD_HEIGHT - 1), (WINDOW_WIDTH, HUD_HEIGHT - 1)
        )

        score_surface = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        level_surface = self.font.render(f"Level: {self.get_level()}", True, TEXT_COLOR)

        self.screen.blit(score_surface, (12, 10))
        self.screen.blit(level_surface, (170, 10))

    def draw_menu(self) -> None:
        for y in range(WINDOW_HEIGHT):
            ratio = y / WINDOW_HEIGHT
            color = (
                int(MENU_GRADIENT_TOP[0] * (1 - ratio) + MENU_GRADIENT_BOTTOM[0] * ratio),
                int(MENU_GRADIENT_TOP[1] * (1 - ratio) + MENU_GRADIENT_BOTTOM[1] * ratio),
                int(MENU_GRADIENT_TOP[2] * (1 - ratio) + MENU_GRADIENT_BOTTOM[2] * ratio),
            )
            pygame.draw.line(self.screen, color, (0, y), (WINDOW_WIDTH, y))

        decor = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(decor, (60, 140, 210, 65), (66, 62), 72)
        pygame.draw.circle(decor, (32, 78, 130, 70), (264, 300), 90)
        pygame.draw.circle(decor, (90, 170, 240, 38), (278, 92), 44)
        self.screen.blit(decor, (0, 0))

        title_y = 72
        title = self.title_font.render("Snake Playground", True, TEXT_COLOR)
        title_shadow = self.title_font.render("Snake Playground", True, (6, 10, 18))
        subtitle = self.small_font.render(
            "Keyboard + Mouse Supported", True, MUTED_TEXT_COLOR
        )
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, title_y))
        shadow_rect = title_shadow.get_rect(center=(WINDOW_WIDTH // 2 + 2, title_y + 2))
        self.screen.blit(title_shadow, shadow_rect)
        self.screen.blit(title, title_rect)
        self.screen.blit(subtitle, subtitle.get_rect(center=(WINDOW_WIDTH // 2, 102)))

        menu_panel = pygame.Rect(28, 144, WINDOW_WIDTH - 56, 182)
        panel_surface = pygame.Surface((menu_panel.width, menu_panel.height), pygame.SRCALPHA)
        panel_surface.fill(MENU_PANEL_COLOR)
        self.screen.blit(panel_surface, menu_panel.topleft)
        pygame.draw.rect(self.screen, GRID_COLOR, menu_panel, width=1, border_radius=14)

        for index, (option, rect) in enumerate(
            zip(self.menu_options, self.get_menu_option_rects())
        ):
            is_selected = index == self.menu_index or index == self.menu_hover_index
            color = (56, 86, 132) if is_selected else BUTTON_COLOR
            text_color = (236, 246, 255) if is_selected else TEXT_COLOR
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            border_color = ACCENT_COLOR if is_selected else GRID_COLOR
            pygame.draw.rect(self.screen, border_color, rect, width=2, border_radius=10)
            option_surface = self.large_font.render(option, True, text_color)
            self.screen.blit(option_surface, option_surface.get_rect(center=rect.center))
            if is_selected:
                indicator = [
                    (rect.x - 12, rect.centery),
                    (rect.x - 2, rect.centery - 7),
                    (rect.x - 2, rect.centery + 7),
                ]
                pygame.draw.polygon(self.screen, ACCENT_COLOR, indicator)

        footer = self.small_font.render(
            "Arrow keys / Enter or mouse click", True, MUTED_TEXT_COLOR
        )
        self.screen.blit(
            footer, footer.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 22))
        )

    def draw_high_scores(self) -> None:
        self.screen.fill(BACKGROUND_COLOR)
        title = self.title_font.render("High Scores", True, TEXT_COLOR)
        self.screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 54)))

        for index, entry in enumerate(self.high_scores, start=1):
            name = str(entry["name"])
            score = int(entry["score"])
            line_rect = pygame.Rect(34, 76 + index * 38, WINDOW_WIDTH - 68, 28)
            line_color = BUTTON_HOVER_COLOR if index == 1 else BUTTON_COLOR
            pygame.draw.rect(self.screen, line_color, line_rect, border_radius=8)
            rank_surface = self.font.render(f"{index}.", True, TEXT_COLOR)
            name_surface = self.font.render(name, True, TEXT_COLOR)
            score_surface = self.font.render(str(score), True, ACCENT_COLOR)
            self.screen.blit(rank_surface, (line_rect.x + 10, line_rect.y + 4))
            self.screen.blit(name_surface, (line_rect.x + 40, line_rect.y + 4))
            self.screen.blit(
                score_surface,
                score_surface.get_rect(
                    midright=(line_rect.right - 12, line_rect.y + 14)
                ),
            )

        footer = self.small_font.render(
            "Press Enter, Space, Backspace, or Esc to return", True, MUTED_TEXT_COLOR
        )
        self.screen.blit(
            footer, footer.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 22))
        )

    def draw_name_entry(self) -> None:
        self.screen.fill(BACKGROUND_COLOR)
        title = self.title_font.render("New High Score", True, ACCENT_COLOR)
        prompt = self.font.render("Enter your name and press Enter", True, TEXT_COLOR)
        score_text = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        name_rect = pygame.Rect(40, 180, WINDOW_WIDTH - 80, 44)
        has_name_text = len(self.name_input) > 0
        display_name = self.name_input if has_name_text else "Type your name"
        name_color = TEXT_COLOR if has_name_text else MUTED_TEXT_COLOR
        name_surface = self.large_font.render(display_name, True, name_color)
        caret_x = name_rect.x + 12 + self.large_font.size(self.name_input)[0]
        caret_x = min(caret_x, name_rect.right - 12)
        length_hint = self.small_font.render(
            f"{len(self.name_input)}/{MAX_NAME_LENGTH}", True, MUTED_TEXT_COLOR
        )
        hint = self.small_font.render(
            "Space and Backspace are supported. Blank name uses Player.",
            True,
            MUTED_TEXT_COLOR,
        )

        self.screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 92)))
        self.screen.blit(prompt, prompt.get_rect(center=(WINDOW_WIDTH // 2, 132)))
        self.screen.blit(score_text, score_text.get_rect(center=(WINDOW_WIDTH // 2, 156)))
        pygame.draw.rect(self.screen, BUTTON_COLOR, name_rect, border_radius=10)
        pygame.draw.rect(self.screen, ACCENT_COLOR, name_rect, width=2, border_radius=10)
        self.screen.blit(name_surface, (name_rect.x + 12, name_rect.y + 9))

        if self.caret_visible:
            pygame.draw.line(
                self.screen,
                TEXT_COLOR,
                (caret_x, name_rect.y + 10),
                (caret_x, name_rect.y + name_rect.height - 10),
                2,
            )

        self.screen.blit(length_hint, (name_rect.right - 56, name_rect.bottom + 8))
        self.screen.blit(hint, hint.get_rect(center=(WINDOW_WIDTH // 2, 272)))

    def draw_game_over(self) -> None:
        overlay = pygame.Surface((WINDOW_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, HUD_HEIGHT))

        game_over_text = self.large_font.render("Game Over", True, GAME_OVER_COLOR)
        restart_text = self.font.render("Enter / R: Restart", True, TEXT_COLOR)
        menu_text = self.font.render("Esc / M: Menu", True, TEXT_COLOR)

        game_center_y = HUD_HEIGHT + GAME_HEIGHT // 2
        self.screen.blit(
            game_over_text,
            game_over_text.get_rect(center=(WINDOW_WIDTH // 2, game_center_y - 24)),
        )
        self.screen.blit(
            restart_text,
            restart_text.get_rect(center=(WINDOW_WIDTH // 2, game_center_y + 18)),
        )
        self.screen.blit(
            menu_text,
            menu_text.get_rect(center=(WINDOW_WIDTH // 2, game_center_y + 44)),
        )

    def draw_playing(self) -> None:
        self.screen.fill(BACKGROUND_COLOR)
        self.draw_grid()
        self.draw_food()
        self.draw_snake()
        self.draw_hud()

        if self.game_over:
            self.draw_game_over()

    def draw(self) -> None:
        if self.state == STATE_MENU:
            self.draw_menu()
        elif self.state == STATE_SCORES:
            self.draw_high_scores()
        elif self.state == STATE_NAME_ENTRY:
            self.draw_name_entry()
        else:
            self.draw_playing()

        pygame.display.flip()

    def run(self) -> None:
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            fps = self.get_speed() if self.state == STATE_PLAYING and not self.game_over else MENU_FPS
            self.clock.tick(fps)

        pygame.quit()


def main() -> None:
    game = SnakeGame()
    game.run()


if __name__ == "__main__":
    main()
