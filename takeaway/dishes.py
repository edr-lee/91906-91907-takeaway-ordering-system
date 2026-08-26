from . import Dish, Drink
from .data import ItemsData

ITEMS = ItemsData().items
DISHES: list[Dish] = [item for item in ITEMS if isinstance(item, Dish)]
DRINKS: list[Drink] = [item for item in ITEMS if isinstance(item, Drink)]
