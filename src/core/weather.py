"""Weather conditions for battles."""

from enum import Enum, auto

class Weather(Enum):
    """Weather conditions that can affect battle."""
    CLEAR = auto()      # No weather effects
    SUN = auto()        # Harsh sunlight
    RAIN = auto()       # Rain
    SANDSTORM = auto()  # Sandstorm
    HAIL = auto()       # Hail
