import tkinter as tk
from pathlib import Path

import customtkinter as ctk
import pygame
from AnimationMenuVM import AnimationMenuVM as amvm
from PIL import Image, ImageTk

# Initialize Pygame (off-screen)
pygame.init()

WIDTH, HEIGHT = 600, 600

# render surface
pygame_surface = pygame.Surface((WIDTH, HEIGHT))


"""Main View of the Animation Editor"""
class AnimationMenuView(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Animation Editor")
        self.geometry("800x700")

        self.running = True

        # Action menu
        self.create_menu()


        # Sprite directory
        self.SPRITE_DIR = Path(__file__).resolve().parent.parent / "assets" / "sprites"

        # Sprite group
        self.sprite_group = pygame.sprite.Group()

        #testing sprite
        file = self.SPRITE_DIR / "Sprite style 2.png"
        self.animation_sprite = SpriteView(
            file,
            (300, 300),
            (128, 128),
        )

        self.sprite_group.add(self.animation_sprite)

        # Preview frame
        self.video_label = ctk.CTkLabel(
            self,
            text=""
        )
        self.video_label.pack(
            expand=True,
            padx=5,
            pady=5,
        )

        # Start rendering
        self.update_pygame_frame()

        # Handle closing
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    """This will create the action menu for more options to get and navigate
    through the animation editor"""
    def create_menu(self):
        # creates the action menu
        action_menu = tk.Menu(self)

        # options in menu initialization
        file_menu = tk.Menu(action_menu, tearoff=0)
        file_menu.add_command(
            label="Add Sprite",
            command=self.open_sprite_browser
        )

        # Create the options and display them on top
        action_menu.add_cascade(label="File", menu=file_menu)

        #attaches itself to the GUI
        self.config(menu=action_menu)

    def render_frame(self):
        # Clear background
        pygame_surface.fill((255, 255, 255))

        #Draw Sprites
        self.sprite_group.draw(pygame_surface)

    def display_frame(self):

        # Convert Pygame surface to PIL
        data = pygame.image.tobytes(pygame_surface, "RGBA")

        pil_image = Image.frombytes("RGBA", (WIDTH, HEIGHT), data)

        # Convert to Tkinter image
        self.tkimage = ImageTk.PhotoImage(image=pil_image)

        # Display
        self.video_label.configure(image=self.tkimage)


    def update_pygame_frame(self):

        if not self.running:
            return

        # self.update_animation()
        self.render_frame()
        self.display_frame()

        # Approximately 60 FPS update the image again
        self.after(16, self.update_pygame_frame)

    def on_close(self):

        self.running = False
        self.destroy()
        pygame.quit()

    def open_sprite_browser(self):
        pass

"""Renders pygame sprites by converting it to PIL immage then to tkinter image"""
class SpriteView(pygame.sprite.Sprite):
    def __init__(self, image_path, position, scale=None):
        super().__init__()


        self.image = amvm.get_image(str(image_path))

        if scale:
            self.image = pygame.transform.scale(self.image, scale)

        self.rect = self.image.get_rect(center=position)

    def set_position(self,x,y):
        self.rect.center = (x,y)

    def update(self):
        pass


if __name__ == "__main__":
    view = AnimationMenuView()
    view.mainloop()