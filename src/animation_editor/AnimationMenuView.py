import os

# Must be set before pygame starts, so no real pygame window ever opens.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


import tkinter as tk
from tkinter import filedialog

import customtkinter as ctk
import pygame
from PIL import Image, ImageTk

from AnimationMenuVM import AnimationMenuVM as amvm



WIDTH, HEIGHT = 600, 600        # size of pygem render surface
ZOOM = 1                        # integer magnification when shown in Tk
FRAME_MS = 33                   # how often the loop checks for changes ~30 per sec
DEFAULT_RECTANGLE = pygame.Rect(50, 50, 200, 100)
IMAGE_TYPES = [("Timages", "*.png *.gif *.bmp"), ("All files", "*.*")]

def surface_to_photo(surf: pygame.Surface, zoom: int = ZOOM) -> ImageTk.PhotoImage:
    """Convert a pygame surface to a Tk-compatible image, keeping alpha."""
    w, h = surf.get_size()
    img = Image.frombytes("RGBA", (w, h), pygame.image.tobytes(surf, "RGBA"))
    if zoom != 1:
        img = img.resize((w * zoom, h * zoom), Image.NEAREST) # NEAREST keeps pixels crisp
    return ImageTk.PhotoImage(img)

def export_gif(frames: list[pygame.Surface], duration_ms: list[int], path) -> None:
    """Write frames to an animated GIF. Durations come from each frame's time_to_next_frame."""
    imgs = [Image.frombytes("RGBA", f.get_size(), pygame.image.tobytes(f, "RGBA"))
            for f in frames]
    imgs[0].save(path,save_all=True, append_images=imgs[1:],
                 duration=duration_ms, loop=0, disposal=2)

"""Renders pygame sprites by converting it to PIL immage then to tkinter image"""
class SpriteView(pygame.sprite.Sprite):
    def __init__(self, image_path, position, scale=None):
        super().__init__()

        self.image = amvm.get_image(str(image_path)).convert_alpha()
        if scale:
            self.image = pygame.transform.scale(self.image, scale)
        self.rect = self.image.get_rect(center=position)

    def set_position(self,x,y):
        self.rect.center = (x,y)



class AnimationMenuView(ctk.CTk):
    """Main View of the Animation Editor"""
    def __init__(self):
        super().__init__()
        self.title("Animation Editor")
        self.geometry("800x700")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        pygame.init()
        pygame.display.set_mode((1, 1))
        self.surface = pygame.Surface((WIDTH, HEIGHT))
        self.sprite_group = pygame.sprite.Group()

        self.dirty = True                       # set True whenever the picture needs redraw
        self._photo = None
        self._after_id = None
        self.create_menu()

        # Canvas insteadof label: it give mouse coordinates and allows overlays later

        self.display = tk.Canvas(self, width=WIDTH * ZOOM,
                                 height=HEIGHT * ZOOM,
                                 highlightthickness=0,
                                 bg="white"
                                 )
        self.display.pack()
        self._image_id = self.display.create_image(0, 0, anchor="nw")

        self._after_id = self.after(FRAME_MS, self.update_pygame_frame)


    #---- menu ----
    def create_menu(self):
        action_menu = tk.Menu(self)

        file_menu = tk.Menu(action_menu, tearoff=0)
        file_menu.add_command(label="Add Sprite...", command=self.open_sprite_browser)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_close)

        action_menu.add_cascade(label="File", menu=file_menu)
        self.config(menu=action_menu)

    def open_sprite_browser(self):
        path = filedialog.askopenfilename(parent=self,
                                          title="Add sprite",
                                          filetypes=IMAGE_TYPES)
        if path:
            self.sprite_group.add(SpriteView(path, (WIDTH // 2, HEIGHT // 2)))
            self.mark_dirty()

    #---- rendering ----
    def mark_dirty(self):
        self.dirty = True

    def render_frame(self):
        # Clear background
        self.surface.fill((255, 255, 255))

        #Draw Sprites
        if self.sprite_group.__len__() == 0:
            pygame.draw.rect(self.surface, (200, 200, 200), DEFAULT_RECTANGLE)
        else:
            self.sprite_group.draw(self.surface)

    def display_frame(self):
        self._photo = surface_to_photo(self.surface)
        self.display.itemconfig(self._image_id, image=self._photo)


    def update_pygame_frame(self):
        if self.dirty:
            self.render_frame()
            self.display_frame()
            self.dirty=False
        self._after_id = self.after(FRAME_MS, self.update_pygame_frame)

    def on_close(self):
        if self._after_id:
            self.after_cancel(self._after_id)
        self.destroy()
        pygame.quit()

if __name__ == "__main__":
    AnimationMenuView().mainloop()