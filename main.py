import pygame
import random
import sys


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
        
        
        shadow_surface = self.font.render(score_text, True, shadow_color)
        self.screen.blit(shadow_surface, (12, 12))
        
      
        main_surface = self.font.render(score_text, True, CYAN)
        self.screen.blit(main_surface, (10, 10))
        
       
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
        
    def game_over_screen(self):
       
        self.screen.fill(BLACK)
        
       
        for i in range(0, self.screen_width, 50):
            for j in range(0, self.screen_height, 50):
                color_intensity = int(30 + 20 * ((i + j) % 100) / 100)
                color = (color_intensity, 0, color_intensity // 2)
                pygame.draw.rect(self.screen, color, (i, j, 25, 25))
        
       
        game_over_text = "GAME OVER!"
        final_score_text = f"Final Score: {self.score}"
        restart_text = "Press R to restart or Q to quit"
        
       
        title_shadow = self.title_font.render(game_over_text, True, (100, 0, 0))
        title_main = self.title_font.render(game_over_text, True, RED)
        title_glow = self.title_font.render(game_over_text, True, ORANGE)
        
        title_x = self.screen_width // 2 - title_main.get_width() // 2
        title_y = self.screen_height // 2 - 80
        
       
        for offset in [(2, 2), (-2, 2), (2, -2), (-2, -2)]:
            self.screen.blit(title_glow, (title_x + offset[0], title_y + offset[1]))
        
        
        self.screen.blit(title_shadow, (title_x + 4, title_y + 4))
      
        self.screen.blit(title_main, (title_x, title_y))
        
     
        score_shadow = self.font.render(final_score_text, True, (80, 80, 80))
        score_main = self.font.render(final_score_text, True, CYAN)
        
        score_x = self.screen_width // 2 - score_main.get_width() // 2
        score_y = self.screen_height // 2 - 20
        
        self.screen.blit(score_shadow, (score_x + 2, score_y + 2))
        self.screen.blit(score_main, (score_x, score_y))
        
       
        restart_shadow = self.font.render(restart_text, True, (60, 60, 60))
        restart_main = self.font.render(restart_text, True, WHITE)
        
        restart_x = self.screen_width // 2 - restart_main.get_width() // 2
        restart_y = self.screen_height // 2 + 40
        
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
                    elif event.key == pygame.K_q:
                        return False
        return False
        
    def run(self):
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