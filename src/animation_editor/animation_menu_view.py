import os

# Must be set before pygame starts, so no real pygame window ever opens.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


import tkinter as tk
from tkinter import filedialog

import customtkinter as ctk
import pygame
from PIL import Image, ImageTk

from src.animation_editor.animation_menu_vm import AnimationMenuVM as amvm

WIDTH, HEIGHT = 600, 600  # size of pygem render surface
ZOOM = 1  # integer magnification when shown in Tk
FRAME_MS = 33  # how often the loop checks for changes ~30 per sec
DEFAULT_RECTANGLE = pygame.Rect(50, 50, 200, 100)
IMAGE_TYPES = [("Timages", "*.png *.gif *.bmp"), ("All files", "*.*")]


def surface_to_photo(surf: pygame.Surface, zoom: int = ZOOM) -> ImageTk.PhotoImage:
    """Convert a pygame surface to a Tk-compatible image, keeping alpha."""
    w, h = surf.get_size()
    img = Image.frombytes("RGBA", (w, h), pygame.image.tobytes(surf, "RGBA"))
    if zoom != 1:
        img = img.resize(
            (w * zoom, h * zoom), Image.Resampling.NEAREST
        )  # NEAREST keeps pixels crisp
    return ImageTk.PhotoImage(img)


def export_gif(frames: list[pygame.Surface], duration_ms: list[int], path) -> None:
    """Write frames to an animated GIF. Durations come from each frame's time_to_next_frame."""
    imgs = [
        Image.frombytes("RGBA", f.get_size(), pygame.image.tobytes(f, "RGBA"))
        for f in frames
    ]
    imgs[0].save(
        path,
        save_all=True,
        append_images=imgs[1:],
        duration=duration_ms,
        loop=0,
        disposal=2,
    )


"""Renders pygame sprites by converting it to PIL immage then to tkinter image"""


class SpriteView(pygame.sprite.Sprite):
    def __init__(self, image_path, position, scale=None):
        super().__init__()

        self.image = amvm.get_image(str(image_path)).convert_alpha()
        if scale:
            self.image = pygame.transform.scale(self.image, scale)
        self.rect = self.image.get_rect(center=position)

    def set_position(self, x, y):
        self.rect.center = (x, y)


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

        self.dirty = True  # set True whenever the picture needs redraw
        self._photo = None
        self._after_id = None
        self.create_menu()

        # Canvas insteadof label: it give mouse coordinates and allows overlays later

        self.display = tk.Canvas(
            self,
            width=WIDTH * ZOOM,
            height=HEIGHT * ZOOM,
            highlightthickness=0,
            bg="white",
        )
        self.display.pack()
        self._image_id = self.display.create_image(0, 0, anchor="nw")

        self._after_id = self.after(FRAME_MS, self.update_pygame_frame)

    # ---- menu ----
    def create_menu(self):
        action_menu = tk.Menu(self)

        file_menu = tk.Menu(action_menu, tearoff=0)
        file_menu.add_command(label="Add Sprite...", command=self.open_sprite_browser)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_close)

        action_menu.add_cascade(label="File", menu=file_menu)
        self.config(menu=action_menu)

    def open_sprite_browser(self):
        path = filedialog.askopenfilename(
            parent=self, title="Add sprite", filetypes=IMAGE_TYPES
        )
        if path:
            self.sprite_group.add(SpriteView(path, (WIDTH // 2, HEIGHT // 2)))
            self.mark_dirty()

    """Animation Frame"""
    def create_animation_frame(self):
        animation_frame = ctk.CTkFrame(self, corner_radius=0)
        animation_frame.grid(row=0, column=0, columnspan=2, rowspan=3, sticky="nsew")

        # configure frame grid
        animation_frame.grid_columnconfigure(0, weight=1)

        # placeholder
        ani_frame_title = ctk.CTkLabel(animation_frame, text="Ani Skin")
        ani_frame_title.grid(row=0, column=0, sticky="nsew")

    # ---- rendering ----
    def mark_dirty(self):
        self.dirty = True

    def render_frame(self):
        # Clear background
        self.surface.fill((255, 255, 255))

        # Draw Sprites
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
            self.dirty = False
        self._after_id = self.after(FRAME_MS, self.update_pygame_frame)

    """Frame Select Frame"""

    # create tabview
    def create_frame_select_tab(self):
        tabview = ctk.CTkTabview(self, width=250)
        tabview.grid(row=0, rowspan=2, column=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        tabview.add("Tab 1")
        tabview.add("Tab 2")

        tabview.tab("Tab 1").grid_columnconfigure(0, weight=1)
        tabview.tab("Tab 1").grid_rowconfigure(0, weight=1)

        tabview.tab("Tab 2").grid_columnconfigure(0, weight=1)

        opt_1_scrollable_frame = ctk.CTkScrollableFrame(tabview.tab("Tab 1"), width=250)
        opt_1_scrollable_frame.grid(row=0, column=0, pady=10, padx=10, sticky="nsew")
        opt_1_scrollable_frame.grid_columnconfigure(0, weight=1)
        for i in range(100):
            frame_container_frame = ctk.CTkFrame(opt_1_scrollable_frame, width=250, fg_color="#505050")
            frame_container_frame.grid(row=i, column=0, padx=5, pady=5, sticky="nsew")

            # Up button
            up_button = ctk.CTkButton(
                frame_container_frame,
                text="▲",
                width=30,
                height=25,
                command=lambda: print("move up")
            )
            up_button.grid(row=0, column=0, padx=5, pady=2)

            # Down button
            down_button = ctk.CTkButton(
                frame_container_frame,
                text="▼",
                width=30,
                height=25,
                command=lambda: print("move down")
            )
            down_button.grid(row=1, column=0, padx=5, pady=2)

            frame_label = ctk.CTkLabel(frame_container_frame, text=f"Frame {i}")
            frame_label.grid(row=0, column=1, padx=5, pady=2)

            frame_label2 = ctk.CTkLabel(frame_container_frame, text=f"Original position Frame {i}")
            frame_label2.grid(row=1, column=1, padx=5, pady=2)

        opt_2_select_frame = ctk.CTkOptionMenu(tabview.tab("Tab 2"), dynamic_resizing=False,
                                               values=["Option 1", "Option 2", "Option 3", "Option 4"])
        opt_2_select_frame.grid(row=0, column=1, sticky="nsew")

        for i in range(50):
            item_list_frame = ctk.CTkFrame(self, width=250)

    """frame pygame prop frame"""

    def create_pygame_prop_frame(self):
        prop_frame = ctk.CTkScrollableFrame(self, width=250)
        prop_frame.grid(row=2, rowspan=2, column=2, padx=(20, 0), pady=(20, 0), sticky="nsew")

        prop_frame.grid_columnconfigure(0, weight=1)

        prop_frame_props = []

        for prop in range(5):
            prop_container_frame = ctk.CTkFrame(prop_frame, fg_color='#505050')
            prop_container_frame.grid(row=prop, column=0, padx=5, pady=5, sticky="nsew")

            ranint = random.randint(1, 100)

            # Create lable for property maybe should be an entry box as well
            label = ctk.CTkLabel(prop_container_frame, text=f"CTkSlider {prop}", width=250)
            label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

            entry = ctk.CTkEntry(prop_container_frame, width=250)
            entry.grid(row=1, column=0, sticky="w")

            # create switch or slider for property
            slider = ctk.CTkSlider(
                prop_container_frame,
                from_=0,
                to=100,
                command=lambda value, e=entry: self.update_entry_from_slider(value, e)
            )
            slider.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
            # remove the scroll functionality of sliders so you can scroll down without messing up values
            slider._canvas.unbind("<MouseWheel>")
            slider._canvas.unbind("<Button-4>")
            slider._canvas.unbind("<Button-5>")
            slider._mouse_wheel_all = lambda event: None

            slider.set(ranint)
            entry.insert(0, str(ranint))
            entry.bind(
                "<Return>",
                lambda event, s=slider, e=entry: self.update_slider_from_entry(s, e)
            )

            prop_frame_props.append(slider)

    def update_entry_from_slider(self, value, entry):
        """Updates the entry text wherever the slider moves."""
        formatted_val = f"{int(round(value))}"
        entry.delete(0, "end")
        entry.insert(0, formatted_val)

    def update_slider_from_entry(self, slider, entry, event=None):
        """Updates the slider wherever the entry."""
        min_val = slider.cget("from_")
        max_val = slider.cget("to")

        try:
            val = float(entry.get())
            # Clamp value within the slider's min/max bounds
            val = max(min_val, min(val, max_val))

            slider.set(val)

            self.update_entry_from_slider(value=val, entry=entry)
        except ValueError:
            # revert entry text to current slider value if input isn't a number
            self.update_entry_from_slider(slider.get(), entry)

    def on_close(self):
        if self._after_id:
            self.after_cancel(self._after_id)
        self.destroy()
        pygame.quit()


if __name__ == "__main__":
    AnimationMenuView().mainloop()
