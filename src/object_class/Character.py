from src.animation.AnimationStack import Action, SpriteDirection


class Character:

    def __init__(self, x=0, y=0, health=100):
        self.x = x
        self.y = y
        self.health = health
        
        # initial state of character
        self.direction = SpriteDirection.S.direction
        self.action = Action.IDLE

    # moves the character by changing its x and y position
    def move(self, x, y):
        self.x += x
        self.y += y

    # lowers the character's health when they take damage
    def take_damage(self, damage):
        self.health -= damage

        # health should not go below 0
        self.health = max(self.health, 0)

    # checks if the character is still alive
    def is_alive(self):
        return self.health > 0
    
    def update_state(self, action: Action, direction: SpriteDirection):
        self.direction = direction
        self.action = action

    #attack1
    def attack(self):
        #TODO build attack call from item
        pass