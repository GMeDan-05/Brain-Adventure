import pygame, time, random
import pygame
import time

class MemoryGame:
    def __init__(self, screen_width, screen_height):
        self.font = pygame.font.SysFont(None, 40)
        # Pairs of data (e.g., 4 pairs = 8 cards)
        self.card_values = ['A', 'A', 'B', 'B', 'C', 'C', 'D', 'D']
        import random
        random.shuffle(self.card_values)
        
        self.cards = []
        # Create a 4x2 grid
        start_x, start_y = screen_width // 4, screen_height // 3
        for i, val in enumerate(self.card_values):
            row, col = i // 4, i % 4
            rect = pygame.Rect(start_x + col * 120, start_y + row * 150, 100, 130)
            self.cards.append({"rect": rect, "value": val, "flipped": False, "matched": False})
            
        self.flipped_cards = []
        self.wait_time = 0

    def handle_click(self, pos):
        # Ignore clicks if we are waiting for cards to flip back
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
            # Set a timer to flip them back after 1 second
            self.wait_time = time.time() + 1.0

    def draw(self, screen):
        # Title
        title = self.font.render("Flip the cards and find a match!", True, (0,0,0))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 100))

        # Handle the delay for flipping cards back
        if self.wait_time > 0 and time.time() > self.wait_time:
            for card in self.flipped_cards:
                card["flipped"] = False
            self.flipped_cards = []
            self.wait_time = 0

        # Draw cards
        for card in self.cards:
            if card["flipped"] or card["matched"]:
                pygame.draw.rect(screen, (255, 255, 255), card["rect"], border_radius=10)
                text = self.font.render(card["value"], True, (0, 0, 0))
                screen.blit(text, text.get_rect(center=card["rect"].center))
            else:
                pygame.draw.rect(screen, (100, 150, 255), card["rect"], border_radius=10) # Card Back

class DragDropGame:
    def __init__(self, screen_width, screen_height):
        self.font = pygame.font.SysFont(None, 50)
        
        # Draggable items: "mon", "key" [cite: 170, 171]
        self.syllables = [
            {"text": "mon", "rect": pygame.Rect(200, 500, 100, 60), "is_dragging": False, "snapped": False},
            {"text": "key", "rect": pygame.Rect(400, 500, 100, 60), "is_dragging": False, "snapped": False}
        ]
        
        # Target drop zones (empty boxes next to the image)
        self.targets = [
            {"rect": pygame.Rect(300, 300, 100, 60), "expected": "mon", "filled": False},
            {"rect": pygame.Rect(420, 300, 100, 60), "expected": "key", "filled": False}
        ]
        self.offset_x = 0
        self.offset_y = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for item in self.syllables:
                if item["rect"].collidepoint(event.pos) and not item["snapped"]:
                    item["is_dragging"] = True
                    self.offset_x = item["rect"].x - event.pos[0]
                    self.offset_y = item["rect"].y - event.pos[1]
                    break # Only drag one at a time
                    
        elif event.type == pygame.MOUSEBUTTONUP:
            for item in self.syllables:
                if item["is_dragging"]:
                    item["is_dragging"] = False
                    # Check if dropped in the correct target
                    for target in self.targets:
                        if target["rect"].colliderect(item["rect"]) and target["expected"] == item["text"]:
                            item["rect"].topleft = target["rect"].topleft # Snap to position
                            item["snapped"] = True
                            target["filled"] = True
                            
        elif event.type == pygame.MOUSEMOTION:
            for item in self.syllables:
                if item["is_dragging"]:
                    item["rect"].x = event.pos[0] + self.offset_x
                    item["rect"].y = event.pos[1] + self.offset_y

    def draw(self, screen):
        title = self.font.render("Drag the correct syllable", True, (0,0,0))
        screen.blit(title, (100, 100))
        
        # Draw Targets (dashed boxes)
        for target in self.targets:
            pygame.draw.rect(screen, (150, 150, 150), target["rect"], 3, border_radius=5)
            
        # Draw Draggable Syllables
        for item in self.syllables:
            color = (100, 255, 100) if item["snapped"] else (255, 200, 100)
            pygame.draw.rect(screen, color, item["rect"], border_radius=5)
            text = self.font.render(item["text"], True, (0,0,0))
            screen.blit(text, text.get_rect(center=item["rect"].center))

            
            
class AudioQuizGame:
    def __init__(self, screen_width, screen_height):
        self.font = pygame.font.SysFont(None, 60)
        self.target_letter = "E" # [cite: 52]
        
        # In a real scenario, load actual audio files:
        # self.audio_e = pygame.mixer.Sound("audio_e.wav")
        # self.audio_a = pygame.mixer.Sound("audio_a.wav")
        
        # Speaker buttons
        self.buttons = [
            {"rect": pygame.Rect(300, 400, 150, 100), "letter": "A", "color": (200, 200, 200)},
            {"rect": pygame.Rect(500, 400, 150, 100), "letter": "E", "color": (200, 200, 200)}
        ]
        self.message = ""

    def handle_click(self, pos):
        for btn in self.buttons:
            if btn["rect"].collidepoint(pos):
                # Play sound associated with this button here
                # pygame.mixer.Sound.play(self.audio_x)
                
                if btn["letter"] == self.target_letter:
                    btn["color"] = (100, 255, 100) # Green for correct
                    self.message = "Correct!"
                else:
                    btn["color"] = (255, 100, 100) # Red for incorrect
                    self.message = "Try Again!"

    def draw(self, screen):
        instruction = self.font.render(f"Find the letter: {self.target_letter}", True, (0,0,0))
        screen.blit(instruction, (200, 150))
        
        for btn in self.buttons:
            pygame.draw.rect(screen, btn["color"], btn["rect"], border_radius=15)
            # Placeholder for speaker icon, using text for now
            icon = self.font.render("Speaker " + btn["letter"], True, (0,0,0))
            screen.blit(icon, icon.get_rect(center=btn["rect"].center))
            
        if self.message:
            msg_surface = self.font.render(self.message, True, (0,0,255))
            screen.blit(msg_surface, (400, 600))