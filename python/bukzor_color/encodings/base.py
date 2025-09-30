"""Base class for color encodings."""

from abc import ABC
from abc import abstractmethod
from typing import Self

from bukzor_color.core import Color


class ColorEncoding(ABC):
    """Abstract base class for color encodings."""

    @abstractmethod
    def decode(self) -> Color:
        """Decode this encoding to a Color."""
        pass

    @classmethod
    @abstractmethod
    def encode(cls, color: Color) -> Self:
        """Encode a Color to this encoding format."""
        pass

    @classmethod
    @abstractmethod
    def parse(cls, text: str) -> Self:
        """Parse text string to this encoding format."""
        pass
