import queue
import threading

import pygame

from src.animation.animation_stack import (
    Action,
    AnimationStack,
    Frame,
    SpriteData,
    SpriteDirection,
)


class Observable:
    """Holds a value and tells subscribers when it changes."""
    def __init__(self, value=None):
        self._value, self._subs = value, []

    def get(self):
        return self._value

    def set(self, value):
        if value != self._value:
            self._value = value
            for callback in self._subs:
                callback(value)

    def subscribe(self, callback):
        self._subs.append(callback)

class AnimationMenuVM:
    def __init__(
        self,
        ani_stack: AnimationStack | None = None,
    ):
        self.ani_stack = ani_stack or AnimationStack()

        self._jobs: queue.Queue = queue.Queue()        # Background tasks for worker thread
        self._events: queue.Queue = queue.Queue()      # Events for UI thread

        self.direction = Observable(SpriteDirection.S)
        self.action = Observable(Action.IDLE)
        self.selected = Observable(None)  # index into the current frame's sprite list
        self.frame_index = Observable(0)  # which frame of the current clip is shown
        self.playing = Observable(False)
        self.changed = Observable(0)  # bumped after any edit to the data

        self._undo: list[tuple] = []  # (do, undo) pairs
        self._redo: list[tuple] = []  # (do, redo) pairs

        self._worker = threading.Thread(target=self._run_thread, name="background-worker", daemon=True)
        self._worker.start()

        self.direction.subscribe(lambda _: self._reset_position())
        self.action.subscribe(lambda _: self._reset_position())

    @staticmethod
    def get_image(filename: str):
        # no need to convert since it is going to be passed through to CustomTkinter
        image = pygame.image.load(str(filename))
        return image



    """---- reading ----"""
    @property
    def frames(self) -> list[Frame]:
        return self.ani_stack.animations[self.direction.get()][self.action.get()]

    @property
    def current_frame(self) -> Frame | None:
        i = self.frame_index.get()
        return self.frames[i] if 0 <= i < len(self.frames) else None

    @property
    def current_sprite(self) -> SpriteData | None:
        frame, i = self.current_frame, self.selected.get()
        if frame is not None and i is not None and 0 <= i < len(frame.sprites):
            return frame.sprites[i]
        return None

    @property
    def can_undo(self) -> bool:
        return bool(self._undo)

    @property
    def can_redo(self) -> bool:
        return bool(self._redo)




    """---- Undo Core ----"""
    def _touch(self):
        self.changed.set(self.changed.get() + 1)

    def _clamp(self):
        """Keep indices valid after an edit or undo changed the list lengths."""
        n = len(self.frames)
        self.frame_index.set(min(max(self.frame_index.get(), 0), max(n - 1, 0)))
        if self.current_sprite is None:
            self.selected.set(None)

    def _push(self, do, undo):
        """Record a command whose effect has already been applied."""
        self._undo.append((do, undo))
        self._redo.clear()
        self._touch()

    def _run(self, do, undo):
        do()
        self._push(do, undo)

    def undo(self):
        if self._undo:
            do, undo = self._undo.pop()
            undo()
            self._redo.append((do, undo))
            self._clamp()
            self._touch()

    def redo(self):
        if self._redo:
            do, undo = self._redo.pop()
            do()
            self._undo.append((do, undo))      # back onto the undo stack
            self._clamp()
            self._touch()

    # resets the position to the original time
    def _reset_position(self):
        self.playing.set(False)
        self._elapsed = 0.0
        self.frame_index.set(0)
        self.selected.set(None)


    """---- Threading Core ----"""
    def _run_thread(self):
        while True:
            job = self._jobs.get()
            if job is None:
                return
            try:
                job()
            except (ValueError, TypeError) as e:
                self._emit("error", f"Something went wrong: {e}")

    def _emit(self, kind: str, payload: object) -> None:
        """
        Update the UI when the worker thread has an error
        """
        self._events.put((kind, payload))


    """---- Indexing Core ----"""
    def move_up_frame(self):
        pass

    def move_down_frame(self):
        pass

    def move_up_layer(self):
        pass

    def move_down_layer(self):
        pass

    def select_frame(self):
        pass

    def select_sprite_layer(self):
        pass



    """---- Transform Action Core ----"""
    def toggle_h_flip(self):
        pass

    def toggle_v_flip(self):
        pass

    def set_scale_x(self, value):
        pass

    def set_scale_y(self, value):
        pass

    def set_image_pos_x(self, value):
        pass

    def set_image_pos_y(self, value):
        pass

    def set_pivot_x(self, value):
        pass

    def set_pivot_y(self, value):
        pass

    def set_pivot_rotation(self, value):
        pass


