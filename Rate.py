from dataclasses import dataclass
from typing import NewType

Seconds = NewType("Seconds", float)

@dataclass
class Rate:
    magnitude: float = 1.0
    window: Seconds = 60.0