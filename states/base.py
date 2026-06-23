# states/base.py

class State:
    def __init__(self):
        self.done = False
        self.quit = False
        self.next_state = None
        
    def startup(self):
        pass

    def get_event(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self, surface):
        pass