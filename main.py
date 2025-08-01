import pygame
import random
import sys
import json
import os
from datetime import datetime


pygame.init()


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
MIN_WIDTH = 600
MIN_HEIGHT = 400
FPS = 60


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)

class Player:
    def __init__(self):
        self.width = 50
        self.height = 40
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - self.height - 10
        self.speed = 5
        self.bullets = []
        
    def move(self, keys, screen_width):
        
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < screen_width - self.width:
            self.x += self.speed
            
    def shoot(self):
    
        bullet = {
            'x': self.x + self.width // 2 - 2,
            'y': self.y,
            'speed': 7
        }
        self.bullets.append(bullet)
        
    def update_bullets(self):
        
        for bullet in self.bullets[:]:  
            bullet['y'] -= bullet['speed']
            if bullet['y'] < 0:
                self.bullets.remove(bullet)
                
    def draw(self, screen):
       
        points = [
            (self.x + self.width // 2, self.y),  
            (self.x, self.y + self.height),      
            (self.x + self.width, self.y + self.height)  
        ]
        pygame.draw.polygon(screen, GREEN, points)
        
        
        for bullet in self.bullets:
            pygame.draw.rect(screen, YELLOW, (bullet['x'], bullet['y'], 4, 10))

class Enemy:
    def __init__(self, screen_width):
        self.width = 40
        self.height = 30
        self.x = random.randint(0, screen_width - self.width)
        self.y = random.randint(-100, -40)
        self.speed = random.randint(2, 4)
        
    def update(self):
       
        self.y += self.speed
        
    def draw(self, screen):
       
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))

class Game:
    def __init__(self):
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
        pygame.display.set_caption("Space Shooter")
        self.clock = pygame.time.Clock()
        self.player = Player()
        self.enemies = []
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 72)
        self.small_font = pygame.font.Font(None, 24)
        self.enemy_spawn_timer = 0
        self.score_history_file = "score_history.json"
        self.score_history = self.load_score_history()
        
    def load_score_history(self):
    
        if os.path.exists(self.score_history_file):
            try:
                with open(self.score_history_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
        
    def save_score_history(self):
        
        try:
            with open(self.score_history_file, 'w') as f:
                json.dump(self.score_history, f, indent=2)
        except:
            pass
            
    def add_score_to_history(self, score):
        """Add a new score to history with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.score_history.append({
            "score": score,
            "date": timestamp
        })
        # Sort by score in descending order
        self.score_history.sort(key=lambda x: x["score"], reverse=True)
        # Keep only top 10 scores
        self.score_history = self.score_history[:10]
        self.save_score_history()
        
    def get_high_score(self):
        """Get the highest score from history"""
        if self.score_history:
            return self.score_history[0]["score"]
        return 0
        
    def handle_resize(self, new_width, new_height):
       
        new_width = max(new_width, MIN_WIDTH)
        new_height = max(new_height, MIN_HEIGHT)
        
        self.screen_width = new_width
        self.screen_height = new_height
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
        
        
        self.player.y = self.screen_height - self.player.height - 10
       

        if self.player.x + self.player.width > self.screen_width:
            self.player.x = self.screen_width - self.player.width
        
    def spawn_enemy(self):
       
        self.enemy_spawn_timer += 1
        if self.enemy_spawn_timer >= 60:
            self.enemies.append(Enemy(self.screen_width))
            self.enemy_spawn_timer = 0
            
    def check_collisions(self):
       
        for bullet in self.player.bullets[:]:
            for enemy in self.enemies[:]:
                if (bullet['x'] < enemy.x + enemy.width and
                    bullet['x'] + 4 > enemy.x and
                    bullet['y'] < enemy.y + enemy.height and
                    bullet['y'] + 10 > enemy.y):
                    
                   
                    self.player.bullets.remove(bullet)
                    self.enemies.remove(enemy)
                    self.score += 10
                    break
                    
       
        for enemy in self.enemies:
            if (self.player.x < enemy.x + enemy.width and
                self.player.x + self.player.width > enemy.x and
                self.player.y < enemy.y + enemy.height and
                self.player.y + self.player.height > enemy.y):
                return True 
                
        return False
        
    def update_enemies(self):
       
        for enemy in self.enemies[:]:
            enemy.update()
            if enemy.y > self.screen_height:
                self.enemies.remove(enemy)
                
    def draw_ui(self):
       
        shadow_color = (50, 50, 50)
        score_text = f"Score: {self.score}"
        high_score_text = f"High Score: {self.get_high_score()}"
        
        
        shadow_surface = self.font.render(score_text, True, shadow_color)
        self.screen.blit(shadow_surface, (12, 12))
        
      
        main_surface = self.font.render(score_text, True, CYAN)
        self.screen.blit(main_surface, (10, 10))
        
        # Draw high score
        high_score_shadow = self.small_font.render(high_score_text, True, shadow_color)
        self.screen.blit(high_score_shadow, (12, 52))
        
        high_score_main = self.small_font.render(high_score_text, True, YELLOW)
        self.screen.blit(high_score_main, (10, 50))
        
       
        instruction_lines = [
            ("Arrow keys to move", WHITE),
            ("Space to shoot", YELLOW),
            ("Avoid red enemies!", RED)
        ]
        
        y_offset = self.screen_height - 80
        for i, (text, color) in enumerate(instruction_lines):
           
            shadow_surface = self.small_font.render(text, True, shadow_color)
            self.screen.blit(shadow_surface, (12, y_offset + i * 25 + 2))
            
           
            text_surface = self.small_font.render(text, True, color)
            self.screen.blit(text_surface, (10, y_offset + i * 25))
            
    def main_menu(self):
        
        menu_running = True
        
        while menu_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        return True  # Start game
                    elif event.key == pygame.K_h:
                        self.show_score_history()
                    elif event.key == pygame.K_q:
                        return False
                elif event.type == pygame.VIDEORESIZE:
                    self.handle_resize(event.w, event.h)
            
           
            self.screen.fill(BLACK)
            
           
            for i in range(0, self.screen_width, 60):
                for j in range(0, self.screen_height, 60):
                    color_intensity = int(20 + 15 * ((i + j + pygame.time.get_ticks() // 50) % 100) / 100)
                    color = (0, color_intensity, color_intensity // 2)
                    pygame.draw.rect(self.screen, color, (i, j, 30, 30))
            
           
            title_text = "SPACE SHOOTER"
            title_shadow = self.title_font.render(title_text, True, (50, 50, 50))
            title_main = self.title_font.render(title_text, True, CYAN)
            
            title_x = self.screen_width // 2 - title_main.get_width() // 2
            title_y = self.screen_height // 2 - 150
            
            self.screen.blit(title_shadow, (title_x + 3, title_y + 3))
            self.screen.blit(title_main, (title_x, title_y))
            
           
            high_score = self.get_high_score()
            high_score_text = f"HIGH SCORE: {high_score}"
            high_score_shadow = self.font.render(high_score_text, True, (80, 80, 0))
            high_score_main = self.font.render(high_score_text, True, YELLOW)
            
            high_score_x = self.screen_width // 2 - high_score_main.get_width() // 2
            high_score_y = self.screen_height // 2 - 80
            
            self.screen.blit(high_score_shadow, (high_score_x + 2, high_score_y + 2))
            self.screen.blit(high_score_main, (high_score_x, high_score_y))
            
            # Menu options
            menu_options = [
                "Press SPACE to start",
                "Press H to view score history", 
                "Press Q to quit"
            ]
            
            y_start = self.screen_height // 2 - 20
            for i, option in enumerate(menu_options):
                option_shadow = self.font.render(option, True, (60, 60, 60))
                option_main = self.font.render(option, True, WHITE)
                
                option_x = self.screen_width // 2 - option_main.get_width() // 2
                option_y = y_start + i * 40
                
                self.screen.blit(option_shadow, (option_x + 2, option_y + 2))
                self.screen.blit(option_main, (option_x, option_y))
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        return False
        
    def show_score_history(self):
      
        history_running = True
        
        while history_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    history_running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                        history_running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.handle_resize(event.w, event.h)
            
            self.screen.fill(BLACK)
            

            for i in range(0, self.screen_width, 40):
                for j in range(0, self.screen_height, 40):
                    color_intensity = int(15 + 10 * ((i + j) % 80) / 80)
                    color = (color_intensity, 0, color_intensity)
                    pygame.draw.rect(self.screen, color, (i, j, 20, 20))
            
            title_text = "SCORE HISTORY"
            title_shadow = self.title_font.render(title_text, True, (80, 0, 80))
            title_main = self.title_font.render(title_text, True, PURPLE)
            
            title_x = self.screen_width // 2 - title_main.get_width() // 2
            title_y = 50
            
            self.screen.blit(title_shadow, (title_x + 3, title_y + 3))
            self.screen.blit(title_main, (title_x, title_y))
            
            header_y = 130
            rank_header = self.font.render("RANK", True, YELLOW)
            score_header = self.font.render("SCORE", True, YELLOW)
            date_header = self.font.render("DATE", True, YELLOW)
            
            self.screen.blit(rank_header, (50, header_y))
            self.screen.blit(score_header, (150, header_y))
            self.screen.blit(date_header, (300, header_y))
            
            # Score history
            if self.score_history:
                for i, entry in enumerate(self.score_history[:10]):
                    y_pos = header_y + 40 + i * 30
                    
                    # Rank
                    rank_text = f"{i + 1}."
                    rank_surface = self.font.render(rank_text, True, WHITE)
                    self.screen.blit(rank_surface, (50, y_pos))
                    
                    # Score
                    score_text = str(entry["score"])
                    score_color = CYAN if i == 0 else WHITE  # Highlight top score
                    score_surface = self.font.render(score_text, True, score_color)
                    self.screen.blit(score_surface, (150, y_pos))
                    
                    # Date
                    date_text = entry["date"]
                    date_surface = self.small_font.render(date_text, True, WHITE)
                    self.screen.blit(date_surface, (300, y_pos))
            else:
                no_scores_text = "No scores recorded yet!"
                no_scores_surface = self.font.render(no_scores_text, True, RED)
                no_scores_x = self.screen_width // 2 - no_scores_surface.get_width() // 2
                self.screen.blit(no_scores_surface, (no_scores_x, 200))
            
            # Instructions
            instruction_text = "Press ESC or BACKSPACE to return"
            instruction_surface = self.small_font.render(instruction_text, True, WHITE)
            instruction_x = self.screen_width // 2 - instruction_surface.get_width() // 2
            self.screen.blit(instruction_surface, (instruction_x, self.screen_height - 50))
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
    def game_over_screen(self):
    
        is_high_score = self.score > self.get_high_score()
        self.add_score_to_history(self.score)
        
        self.screen.fill(BLACK)
        
       
        for i in range(0, self.screen_width, 50):
            for j in range(0, self.screen_height, 50):
                color_intensity = int(30 + 20 * ((i + j) % 100) / 100)
                color = (color_intensity, 0, color_intensity // 2)
                pygame.draw.rect(self.screen, color, (i, j, 25, 25))
        
       
        game_over_text = "GAME OVER!"
        final_score_text = f"Final Score: {self.score}"
        high_score_text = f"High Score: {self.get_high_score()}"
        new_record_text = "NEW HIGH SCORE!" if is_high_score else ""
        restart_text = "Press R to restart, H for history, or Q to quit"
        
       
        title_shadow = self.title_font.render(game_over_text, True, (100, 0, 0))
        title_main = self.title_font.render(game_over_text, True, RED)
        title_glow = self.title_font.render(game_over_text, True, ORANGE)
        
        title_x = self.screen_width // 2 - title_main.get_width() // 2
        title_y = self.screen_height // 2 - 120
        
       
        for offset in [(2, 2), (-2, 2), (2, -2), (-2, -2)]:
            self.screen.blit(title_glow, (title_x + offset[0], title_y + offset[1]))
        
        
        self.screen.blit(title_shadow, (title_x + 4, title_y + 4))
      
        self.screen.blit(title_main, (title_x, title_y))
        
        # New high score notification
        if new_record_text:
            record_shadow = self.font.render(new_record_text, True, (120, 120, 0))
            record_main = self.font.render(new_record_text, True, YELLOW)
            
            record_x = self.screen_width // 2 - record_main.get_width() // 2
            record_y = self.screen_height // 2 - 70
            
            self.screen.blit(record_shadow, (record_x + 2, record_y + 2))
            self.screen.blit(record_main, (record_x, record_y))
        
     
        score_shadow = self.font.render(final_score_text, True, (80, 80, 80))
        score_main = self.font.render(final_score_text, True, CYAN)
        
        score_x = self.screen_width // 2 - score_main.get_width() // 2
        score_y = self.screen_height // 2 - 30
        
        self.screen.blit(score_shadow, (score_x + 2, score_y + 2))
        self.screen.blit(score_main, (score_x, score_y))
        
        # High score display
        high_score_shadow = self.font.render(high_score_text, True, (80, 80, 0))
        high_score_main = self.font.render(high_score_text, True, YELLOW)
        
        high_score_x = self.screen_width // 2 - high_score_main.get_width() // 2
        high_score_y = self.screen_height // 2 + 10
        
        self.screen.blit(high_score_shadow, (high_score_x + 2, high_score_y + 2))
        self.screen.blit(high_score_main, (high_score_x, high_score_y))
        
       
        restart_shadow = self.font.render(restart_text, True, (60, 60, 60))
        restart_main = self.font.render(restart_text, True, WHITE)
        
        restart_x = self.screen_width // 2 - restart_main.get_width() // 2
        restart_y = self.screen_height // 2 + 60
        
        self.screen.blit(restart_shadow, (restart_x + 2, restart_y + 2))
        self.screen.blit(restart_main, (restart_x, restart_y))
        
        pygame.display.flip()
        
       
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        
                        self.__init__()
                        return True
                    elif event.key == pygame.K_h:
                        self.show_score_history()
                    elif event.key == pygame.K_q:
                        return False
        return False
        
    def run(self):
        # Show main menu first
        if not self.main_menu():
            pygame.quit()
            sys.exit()
            
        running = True
        
        while running:
           
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.player.shoot()
                elif event.type == pygame.VIDEORESIZE:
                   
                    self.handle_resize(event.w, event.h)
                        
            
            keys = pygame.key.get_pressed()
            
           
            self.player.move(keys, self.screen_width)
            self.player.update_bullets()
            self.spawn_enemy()
            self.update_enemies()
            
           
            if self.check_collisions():
                if not self.game_over_screen():
                    running = False
                continue
            
          
            self.screen.fill(BLACK)
            self.player.draw(self.screen)
            
            for enemy in self.enemies:
                enemy.draw(self.screen)
                
            self.draw_ui()
            
    
            pygame.display.flip()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()