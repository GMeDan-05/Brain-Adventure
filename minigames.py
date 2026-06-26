import pygame
import time
import random
import os

# --- Helper Function for Robust Asset Loading ---
def load_sprite(path, size, fallback_color=(150, 150, 150)):
    """Tries to load an image. If it fails, returns a colored surface of the same size."""
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.smoothscale(img, size)
    except FileNotFoundError:
        print(f"[WARNING] Missing asset: {path}. Using fallback color.")
        surf = pygame.Surface(size)
        surf.fill(fallback_color)
        return surf

class MemoryGame:
    def __init__(self, screen_width, screen_height, pairs=3):
        self.font = pygame.font.SysFont(None, 40)
        self.width = screen_width
        self.height = screen_height
        
        # --- Load Assets ---
        self.bg_img = load_sprite("assets/images/BG.jpg", (self.width, self.height), (200, 230, 255))
        self.card_back = load_sprite("assets/images/card_back.png", (120, 150), (100, 150, 255))
        self.card_front_bg = load_sprite("assets/images/card_front.png", (120, 150), (255, 255, 255))
        
        # Generate pairs dynamically
        base_values = ['Cat', 'Dog', 'Bird', 'Fish', 'Cow', 'Sheep']
        self.card_values = base_values[:pairs] * 2
        random.shuffle(self.card_values)
        
        self.cards = []
        cols = 3 if pairs == 3 else 4
        
        start_x, start_y = screen_width // 3, screen_height // 3
        for i, val in enumerate(self.card_values):
            row, col = i // cols, i % cols
            rect = pygame.Rect(start_x + col * 150, start_y + row * 180, 120, 150)
            self.cards.append({"rect": rect, "value": val, "flipped": False, "matched": False})
            
        self.flipped_cards = []
        self.wait_time = 0

    def handle_click(self, pos):
        if self.wait_time > 0: return

        for card in self.cards:
            if card["rect"].collidepoint(pos) and not card["flipped"] and not card["matched"]:
                card["flipped"] = True
                self.flipped_cards.append(card)
                
                if len(self.flipped_cards) == 2:
                    self.check_match()
                break

    def check_match(self):
        card1, card2 = self.flipped_cards
        if card1["value"] == card2["value"]:
            card1["matched"] = True
            card2["matched"] = True
            self.flipped_cards = []
        else:
            self.wait_time = time.time() + 1.0

    def draw(self, screen):
        # Draw Background
        screen.blit(self.bg_img, (0, 0))
        
        # Title
        title = self.font.render("Find the matching pairs!", True, (0, 0, 0))
        title_rect = title.get_rect(center=(self.width // 2, 100))
        
        # Add a subtle background behind the text so it's readable on any background
        title_bg = pygame.Surface((title_rect.width + 20, title_rect.height + 10))
        title_bg.fill((255, 255, 255))
        title_bg.set_alpha(180)
        screen.blit(title_bg, title_rect.move(-10, -5))
        screen.blit(title, title_rect)

        # Logic for flipping cards back over
        if self.wait_time > 0 and time.time() > self.wait_time:
            for card in self.flipped_cards:
                card["flipped"] = False
            self.flipped_cards = []
            self.wait_time = 0

        # Draw Cards
        for card in self.cards:
            if card["flipped"] or card["matched"]:
                # Draw front sprite
                screen.blit(self.card_front_bg, card["rect"].topleft)
                text = self.font.render(card["value"], True, (0, 0, 0))
                screen.blit(text, text.get_rect(center=card["rect"].center))
            else:
                # Draw back sprite
                screen.blit(self.card_back, card["rect"].topleft)


class DragDropGame:
    def __init__(self, screen_width, screen_height):
        self.font = pygame.font.SysFont(None, 50)
        self.width = screen_width
        self.height = screen_height
        
        # --- Load Assets ---
        self.bg_img = load_sprite("assets/images/BG.jpg", (self.width, self.height), (240, 240, 240))
        self.syllable_bg = load_sprite("assets/images/btn_syllable.png", (120, 70), (255, 200, 100))
        self.syllable_bg_snapped = load_sprite("assets/images/btn_syllable_correct.png", (120, 70), (100, 255, 100))
        self.target_bg = load_sprite("assets/images/box_dashed.png", (120, 70), (200, 200, 200))
        self.main_graphic = load_sprite("assets/images/monkey.png", (200, 200), (180, 180, 180)) # [cite: 63, 64]
        
        self.syllables = [
            {"text": "mon", "rect": pygame.Rect(self.width//2 - 150, 500, 120, 70), "is_dragging": False, "snapped": False},
            {"text": "key", "rect": pygame.Rect(self.width//2 + 50, 500, 120, 70), "is_dragging": False, "snapped": False}
        ]
        
        self.targets = [
            {"rect": pygame.Rect(self.width//2 - 130, 350, 120, 70), "expected": "mon", "filled": False},
            {"rect": pygame.Rect(self.width//2 + 10, 350, 120, 70), "expected": "key", "filled": False}
        ]
        self.offset_x = 0
        self.offset_y = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check syllables in reverse order so top drawn items are dragged first
            for item in reversed(self.syllables):
                if item["rect"].collidepoint(event.pos) and not item["snapped"]:
                    item["is_dragging"] = True
                    self.offset_x = item["rect"].x - event.pos[0]
                    self.offset_y = item["rect"].y - event.pos[1]
                    break 
                    
        elif event.type == pygame.MOUSEBUTTONUP:
            for item in self.syllables:
                if item["is_dragging"]:
                    item["is_dragging"] = False
                    for target in self.targets:
                        if target["rect"].colliderect(item["rect"]) and target["expected"] == item["text"]:
                            item["rect"].topleft = target["rect"].topleft
                            item["snapped"] = True
                            target["filled"] = True
                            
        elif event.type == pygame.MOUSEMOTION:
            for item in self.syllables:
                if item["is_dragging"]:
                    item["rect"].x = event.pos[0] + self.offset_x
                    item["rect"].y = event.pos[1] + self.offset_y

    def draw(self, screen):
        screen.blit(self.bg_img, (0, 0))
        
        title = self.font.render("Drag the correct syllable", True, (0, 0, 0))
        screen.blit(title, (self.width//2 - title.get_width()//2, 100))
        
        # Draw the main graphic (e.g., picture of the monkey)
        screen.blit(self.main_graphic, (self.width//2 - 100, 130))
        
        # Draw Targets
        for target in self.targets:
            screen.blit(self.target_bg, target["rect"].topleft)
            
        # Draw Draggable Syllables
        for item in self.syllables:
            # Choose sprite based on whether it is snapped correctly
            bg_to_draw = self.syllable_bg_snapped if item["snapped"] else self.syllable_bg
            screen.blit(bg_to_draw, item["rect"].topleft)
            
            text = self.font.render(item["text"], True, (0, 0, 0))
            screen.blit(text, text.get_rect(center=item["rect"].center))


class AudioQuizGame:
    def __init__(self, screen_width, screen_height):
        self.font = pygame.font.SysFont(None, 60)
        self.width = screen_width
        self.height = screen_height
        self.target_letter = "A" 
        
        # --- Load Assets ---
        self.bg_img = load_sprite("assets/images/BG.jpg", (self.width, self.height), (255, 240, 200))
        self.btn_img = load_sprite("assets/images/btn_option.png", (150, 150), (220, 220, 220))
        self.speaker_icon = load_sprite("assets/images/speaker_icon.png", (60, 60), (100, 100, 100))
        
        # Spacing logic [cite: 74-90]
        start_x = self.width // 2 - 250
        self.buttons = [
            {"rect": pygame.Rect(start_x, 350, 150, 150), "letter": "A", "color_tint": None},
            {"rect": pygame.Rect(start_x + 200, 350, 150, 150), "letter": "B", "color_tint": None},
            {"rect": pygame.Rect(start_x + 400, 350, 150, 150), "letter": "C", "color_tint": None}
        ]
        self.message = ""

    def handle_click(self, pos):
        for btn in self.buttons:
            if btn["rect"].collidepoint(pos):
                if btn["letter"] == self.target_letter:
                    btn["color_tint"] = (100, 255, 100) # Green tint flag
                    self.message = "Betul!"
                else:
                    btn["color_tint"] = (255, 100, 100) # Red tint flag
                    self.message = "Cuba Lagi!"

    def draw(self, screen):
        screen.blit(self.bg_img, (0, 0))
        
        instruction = self.font.render("Dengar dan pilih huruf yang betul", True, (0, 0, 0))
        screen.blit(instruction, (self.width//2 - instruction.get_width()//2, 150))
        
        # Main big speaker button for the question
        main_speaker_rect = self.speaker_icon.get_rect(center=(self.width//2, 250))
        screen.blit(self.speaker_icon, main_speaker_rect)
        
        for btn in self.buttons:
            # If standard, draw normal button. If clicked, we can draw a tinted rectangle behind it
            if btn["color_tint"]:
                pygame.draw.rect(screen, btn["color_tint"], btn["rect"].inflate(10, 10), border_radius=20)
                
            screen.blit(self.btn_img, btn["rect"].topleft)
            
            icon = self.font.render(btn["letter"], True, (0, 0, 0))
            screen.blit(icon, icon.get_rect(center=btn["rect"].center))
            
        if self.message:
            msg_color = (0, 180, 0) if self.message == "Betul!" else (200, 0, 0)
            msg_surface = self.font.render(self.message, True, msg_color)
            screen.blit(msg_surface, (self.width//2 - msg_surface.get_width()//2, 550))