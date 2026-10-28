from typing import Callable, Any

class Observable:
    """Handles event subscriptions and broadcasts."""
    def __init__(self):
        self._observers: list[Callable[..., None]] = []

    def subscribe(self, callback: Callable[..., None]):
        self._observers.append(callback)

    def emit(self, *args, **kwargs):
        for callback in self._observers:
            callback(*args, **kwargs)

class BindableProperty:
    """A descriptor that automatically fires update events when data changes."""
    def __init__(self, default: Any = None):
        self.name = ""
        self.default = default

    def __set_name__(self, owner, name):
        self.name = f"_{name}"

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.name, self.default)

    def __set__(self, instance, value):
        old_value = getattr(instance, self.name, self.default)
        if old_value != value:
            setattr(instance, self.name, value)
            # Notify the ViewModel's property changed stream
            if hasattr(instance, "property_changed"):
                instance.property_changed.emit(self.name.lstrip("_"), value)

class ViewModelBase:
    """Base class providing property notification mechanisms."""
    def __init__(self):
        self.property_changed = Observable()

class RelayCommand:
    """Encapsulates a UI action or button click."""
    def __init__(self, action: Callable[[], None], can_execute: Callable[[], bool] = lambda: True):
        self.action = action
        self.can_execute = can_execute

    def execute(self):
        if self.can_execute():
            self.action()
