"""Takeaway classes."""

from __future__ import annotations

from abc import ABC


class Item(ABC):
    """Represents an item in the cart."""

    name: str
    """Name of the item."""
    price_without_tax: float
    """The price of the item excluding tax."""
    image_filename: str
    """Image filename for displaying this item in the UI."""


class Dish(Item):
    """Represents a meal item."""

    def __init__(self, name: str, price_without_tax: float, image_filename: str):
        self.name = name
        self.price_without_tax = price_without_tax
        self.image_filename = image_filename

    def __str__(self) -> str:
        return f"{self.name}: ${self.price_without_tax:.2f}"


class Drink(Item):
    """Represents a drink item."""

    size: str
    """Size of the drink."""

    def __init__(
        self, name: str, price_without_tax: float, size: str, image_filename: str
    ):
        self.name = name
        self.price_without_tax = price_without_tax
        self.size = size
        self.image_filename = image_filename

    def __str__(self) -> str:
        return f"{self.name} ({self.size}): ${self.price_without_tax:.2f}"
