import customtkinter as ctk
import pygame
from PIL import Image, ImageTk

# Initialize Pygame (off-screen / headless-style surface or hidden window)
pygame.init()
WIDTH, HEIGHT = 400, 400
pygame_surface = pygame.Surface((WIDTH, HEIGHT))

# Create a Pygame Sprite
class PlayerSprite(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Create a simple colored surface for the sprite (or load an image via pygame.image.load)
        self.image = pygame.Surface((50, 50))
        self.image.fill((255, 87, 51)) # Orange color
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    def update(self):
        # Example movement or logic
        self.rect.x = (self.rect.x + 1) % WIDTH

sprite_group = pygame.sprite.Group()
player = PlayerSprite()
sprite_group.add(player)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Pygame Sprite in CustomTkinter")
        self.geometry("500x500")

        # Create a CustomTkinter Label to hold the Pygame frame
        self.video_label = ctk.CTkLabel(self, text="")
        self.video_label.pack(expand=True, padx=20, pady=20)

        self.update_pygame_frame()

    def update_pygame_frame(self):
        # 1. Update Pygame sprite logic
        sprite_group.update()

        # 2. Draw everything onto our Pygame surface
        pygame_surface.fill((30, 30, 30)) # Background color
        sprite_group.draw(pygame_surface)

        # 3. Convert Pygame surface to string/buffer, then to PIL Image
        # pygame.image.tostring is deprecated in newer pygame; use pygame.image.tobytes
        data = pygame.image.tobytes(pygame_surface, "RGB")
        pil_image = Image.frombytes("RGB", (WIDTH, HEIGHT), data)

        # 4. Convert PIL Image to CustomTkinter / Tkinter compatible PhotoImage
        self.tk_image = ImageTk.PhotoImage(image=pil_image)

        # 5. Update the CTkLabel image
        self.video_label.configure(image=self.tk_image)

        # 6. Schedule the next frame update (e.g., ~30-60 FPS -> 30ms)
        self.after(30, self.update_pygame_frame)

if __name__ == "__main__":
    app = App()
    app.mainloop()
