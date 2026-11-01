import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bob")
clock = pygame.time.Clock()

AZZURRO_CIELO = (135, 206, 235)
GIALLO_BOB = (255, 255, 0)
VERDE_TUBO = (34, 139, 34)
BIANCO = (255, 255, 255)
GRIGIO = (100, 100, 100)
ROSSO = (255, 0, 0)

gravity = 0.25
bird_movement = 0
game_active = False
game_started = False  # Nuovo: traccia se siamo passati dal menù
score = 0
pipe_passed = set()

bob_rect = pygame.Rect(50, 300, 35, 35)
pipe_list = []
SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, 1200)
pipe_height = [200, 300, 400]

# ===== MENÙ =====
class Button:
    """Classe per i pulsanti del menù"""
    def __init__(self, x, y, width, height, text, color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.hover = False

    def draw(self, surface):
        # Cambia colore al hover
        color = tuple(min(c + 50, 255) for c in self.color) if self.hover else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BIANCO, self.rect, 3, border_radius=10)
        
        # Rendering testo
        font = pygame.font.SysFont("Arial", 25, bold=True)
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def update(self, pos):
        self.hover = self.rect.collidepoint(pos)

def draw_menu():
    """Disegna il menù principale"""
    screen.fill(AZZURRO_CIELO)
    
    # Titolo
    title_font = pygame.font.SysFont("Arial", 60, bold=True)
    title = title_font.render("FLAPPY BOB", True, GIALLO_BOB)
    title_rect = title.get_rect(center=(WIDTH // 2, 100))
    screen.blit(title, title_rect)
    
    # Sottotitolo
    subtitle_font = pygame.font.SysFont("Arial", 20)
    subtitle = subtitle_font.render("Un gioco di abilità", True, BIANCO)
    subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, 160))
    screen.blit(subtitle, subtitle_rect)
    
    # Disegna i pulsanti
    start_button.draw(screen)
    instructions_button.draw(screen)
    quit_button.draw(screen)

def draw_instructions():
    """Disegna la schermata delle istruzioni"""
    screen.fill(AZZURRO_CIELO)
    
    # Titolo
    title_font = pygame.font.SysFont("Arial", 40, bold=True)
    title = title_font.render("ISTRUZIONI", True, GIALLO_BOB)
    title_rect = title.get_rect(center=(WIDTH // 2, 50))
    screen.blit(title, title_rect)
    
    # Testo istruzioni
    instructions_text = [
        "🎯 Obiettivo:",
        "Evita i tubi verde!",
        "",
        "⌨️  Controlli:",
        "SPACE = Salta",
        "",
        "💡 Consigli:",
        "- Timing perfetto",
        "- Evita i bordi",
        "- Raccogli più punti",
    ]
    
    font = pygame.font.SysFont("Arial", 18)
    y_offset = 130
    for line in instructions_text:
        if line == "":
            y_offset += 10
        else:
            text = font.render(line, True, BIANCO)
            text_rect = text.get_rect(center=(WIDTH // 2, y_offset))
            screen.blit(text, text_rect)
            y_offset += 35
    
    # Pulsante back
    back_button.draw(screen)

def create_pipe():
    random_pipe_pos = random.choice(pipe_height)
    bottom_pipe = pygame.Rect(400, random_pipe_pos, 50, 600)
    top_pipe = pygame.Rect(400, random_pipe_pos - 150 - 600, 50, 600)
    return bottom_pipe, top_pipe

def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= 3
    return [pipe for pipe in pipes if pipe.right > -50]

def draw_pipes(pipes):
    for pipe in pipes:
        pygame.draw.rect(screen, VERDE_TUBO, pipe)

def check_collision(pipes):
    for pipe in pipes:
        if bob_rect.colliderect(pipe):
            return False
    if bob_rect.top <= 0 or bob_rect.bottom >= 600:
        return False
    return True

def reset_game():
    """Resetta il gioco"""
    global game_active, score, pipe_passed, bird_movement
    game_active = True
    score = 0
    pipe_passed.clear()
    pipe_list.clear()
    bob_rect.center = (50, 300)
    bird_movement = 0

# ===== STATO DEL GIOCO =====
MENU = 0
INSTRUCTIONS = 1
PLAYING = 2
GAME_OVER = 3

current_state = MENU

# ===== PULSANTI =====
start_button = Button(50, 250, 300, 60, "GIOCA", (34, 139, 34), BIANCO)
instructions_button = Button(50, 340, 300, 60, "ISTRUZIONI", (70, 130, 180), BIANCO)
quit_button = Button(50, 430, 300, 60, "ESCI", (180, 50, 50), BIANCO)
back_button = Button(50, 500, 300, 60, "INDIETRO", (100, 100, 100), BIANCO)
restart_button = Button(50, 430, 300, 60, "RICOMINCIA", (34, 139, 34), BIANCO)
menu_button = Button(50, 500, 300, 60, "MENÙ", (100, 100, 100), BIANCO)

# ===== LOOP PRINCIPALE =====
while True:
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        # ===== MENÙ PRINCIPALE =====
        if current_state == MENU:
            start_button.update(mouse_pos)
            instructions_button.update(mouse_pos)
            quit_button.update(mouse_pos)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.is_clicked(mouse_pos):
                    reset_game()
                    current_state = PLAYING
                elif instructions_button.is_clicked(mouse_pos):
                    current_state = INSTRUCTIONS
                elif quit_button.is_clicked(mouse_pos):
                    pygame.quit()
                    sys.exit()
        
        # ===== ISTRUZIONI =====
        elif current_state == INSTRUCTIONS:
            back_button.update(mouse_pos)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.is_clicked(mouse_pos):
                    current_state = MENU
        
        # ===== GIOCO =====
        elif current_state == PLAYING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game_active:
                    bird_movement = -6
                elif event.key == pygame.K_ESCAPE:
                    current_state = MENU

            if event.type == SPAWNPIPE:
                pipe_list.extend(create_pipe())
        
        # ===== GAME OVER =====
        elif current_state == GAME_OVER:
            restart_button.update(mouse_pos)
            menu_button.update(mouse_pos)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button.is_clicked(mouse_pos):
                    reset_game()
                    current_state = PLAYING
                elif menu_button.is_clicked(mouse_pos):
                    current_state = MENU
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    current_state = MENU

    # ===== DISEGNA MENÙ =====
    if current_state == MENU:
        draw_menu()
    
    # ===== DISEGNA ISTRUZIONI =====
    elif current_state == INSTRUCTIONS:
        draw_instructions()
    
    # ===== DISEGNA GIOCO =====
    elif current_state == PLAYING:
        screen.fill(AZZURRO_CIELO)
        
        if game_active:
            # Fisica di Bob
            bird_movement += gravity
            bob_rect.centery += bird_movement
            pygame.draw.rect(screen, GIALLO_BOB, bob_rect)
            
            # Gestione Tubi
            pipe_list = move_pipes(pipe_list)
            draw_pipes(pipe_list)
            
            # Conteggio score
            for pipe in pipe_list:
                if 400 < pipe.centerx < 403 and id(pipe) not in pipe_passed:
                    score += 1
                    pipe_passed.add(id(pipe))
            
            # Collisioni
            game_active = check_collision(pipe_list)
            
            if not game_active:
                current_state = GAME_OVER
            
            # Mostra score
            font = pygame.font.SysFont("Arial", 25, bold=True)
            score_text = font.render(f"Score: {score}", True, BIANCO)
            screen.blit(score_text, (10, 10))
            
            # Istruzioni escape
            small_font = pygame.font.SysFont("Arial", 14)
            escape_text = small_font.render("ESC per tornare al menù", True, BIANCO)
            screen.blit(escape_text, (10, HEIGHT - 25))
    
    # ===== DISEGNA GAME OVER =====
    elif current_state == GAME_OVER:
        screen.fill(AZZURRO_CIELO)
        
        # Disegna Bob e tubi di fondo (effetto sfumato)
        pygame.draw.rect(screen, GIALLO_BOB, bob_rect, alpha=100)
        for pipe in pipe_list[:5]:
            pygame.draw.rect(screen, VERDE_TUBO, pipe)
        
        # Titolo Game Over
        title_font = pygame.font.SysFont("Arial", 50, bold=True)
        game_over_title = title_font.render("GAME OVER", True, ROSSO)
        title_rect = game_over_title.get_rect(center=(WIDTH // 2, 80))
        screen.blit(game_over_title, title_rect)
        
        # Score finale
        score_font = pygame.font.SysFont("Arial", 35, bold=True)
        score_display = score_font.render(f"Score: {score}", True, GIALLO_BOB)
        score_rect = score_display.get_rect(center=(WIDTH // 2, 160))
        screen.blit(score_display, score_rect)
        
        # Pulsanti
        restart_button.draw(screen)
        menu_button.draw(screen)

    pygame.display.update()
    clock.tick(60)
 